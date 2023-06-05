import boto3
import os
import cv2
import numpy as np
import io

# YOLO setup
net = cv2.dnn.readNet("/opt/yolo_tiny_configs/yolov3-tiny.weights", "/opt/yolo_tiny_configs/yolov3-tiny.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().tolist()]

classes = []
with open("/opt/yolo_tiny_configs/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Create a connection to the S3 service
s3 = boto3.client('s3')

# Create a connection to the DynamoDB service
dynamodb = boto3.resource('dynamodb')

# Connect to the DynamoDB table
table = dynamodb.Table('image-info-table')

# Define S3 bucket to a variable 
bucket = 'imagefile-storage'

def handle_image_upload(bucket, key):
    # Retrieve the image from S3
    s3_response_object = s3.get_object(Bucket=bucket, Key=key)
    object_content = s3_response_object['Body'].read()

    # Load image with OpenCV
    nparr = np.frombuffer(object_content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform object detection with YOLO
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                class_ids.append(class_id)
    
    return [classes[id] for id in class_ids] if class_ids else []

def lambda_handler(event, context):
    if 'Records' in event:
        # Scenario 1: Image upload triggered by S3
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # Save image info to the DynamoDB
        image_info = {
            'image-url': f"s3://{bucket}/{key}",
            'tags': handle_image_upload(bucket, key)
        }
        
        try:
            table.put_item(Item=image_info)
        except Exception as e:
            print(f"Error putting item into DynamoDB: {e}")
        
        return {
            'statusCode': 200,
            'body': "Image processed successfully and saved into the DynamoDB"
        }
    
    elif 'httpMethod' in event:
        # Scenario 2: API call with image as PUT method
        http_method = event['httpMethod']

        if http_method == 'GET':
            body = event['body']
            
            if body:
                tags = handle_image_upload(body)
            
            response = {
                'tags': tags
            }
            return {
                'statusCode': 200,
                'body': json.dumps(response)
            }
        else:
            # Invalid HTTP method
            return {
                'statusCode': 400,
                'body': 'Invalid HTTP method'
            }

        # Find matching images based on tags and counts
        response = table.scan()
        images = response['Items']
        matching_images = []

        for image in images:
            image_tags = image.get('tags', [])

            if isinstance(image_tags, str):
                # Tags are stored as a string, convert to a list
                image_tags = [t.strip() for t in image_tags[1:-1].split(',')]

            is_match = True

            for tag in tags:
                tag_name = tag['tag']
                tag_count = max(tag.get('count', 1), 1)  # Set a minimum count of 1 if count is not mentioned

                if image_tags.count(tag_name) < tag_count:
                    is_match = False
                    break

            if is_match:
                matching_images.append(image['image-url'])

        # Prepare the response
        response = {
            'links': matching_images
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    
    else:
        # Invalid event type
        return {
            'statusCode': 400,
            'body': "Invalid event type."
        }
