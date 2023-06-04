// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'us-east-1';
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
  IdentityPoolId: 'us-east-1:695e586b-8699-435b-bc68-acdf9621df36'
});

// Handle the form submission
document.getElementById('signInForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent form submission

  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;

  var authenticationData = {
    Username: username,
    Password: password
  };

  var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);

  var poolData = {
    UserPoolId: 'us-east-1_eJOXxbQbM',
    ClientId: '42qs0totfpegq11p60ej4pthgo'
  };

  var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

  var userData = {
    Username: username,
    Pool: userPool
  };

  var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

  cognitoUser.authenticateUser(authenticationDetails, {
    onSuccess: function(result) {
      // Store user data in localStorage after a successful authentication
      localStorage.setItem('CognitoUser', JSON.stringify({
        Username: username,
        UserPoolId: poolData.UserPoolId,
        ClientId: poolData.ClientId
      }));
  
      window.location.href = 'upload.html'; // Redirect to success page
    },
    onFailure: function(err) {
      alert('Sign-in failed. Please try again.'); // Display error message
    }
  });
});
