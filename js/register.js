document.getElementById('signUpForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
  
    var username = document.getElementById('username').value;
    var givenname = document.getElementById('givenname').value;
    var familyname = document.getElementById('familyname').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
  
    var poolData = {
        UserPoolId: 'us-east-1_eJOXxbQbM',
        ClientId: '42qs0totfpegq11p60ej4pthgo'
    };
  
    var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
  
    var attributeList = [
      new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'given_name', Value: givenname }),
      new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'family_name', Value: familyname }),
      new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'email', Value: email })
    ];
  
    userPool.signUp(username, password, attributeList, null, function(err, result) {
      if (err) {
        alert(err.message || JSON.stringify(err));
        return;
      }
      console.log('User registration successful');
      window.location.href = 'success.html'; // Redirect to success page
    });
  });
  