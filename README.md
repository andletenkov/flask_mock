# mock-server

# Requirements
Docker need to be installed

# How to
1. Deploy service to host (or run it locally)
2. Implement custom JSON schema, put it to /schemas directory (or use "example.json" for test)
3. Execute GET {host:port}/example/users/666
4. Obtain response: "\"id\": 666, \"name\": \"John Wick\", \"email\": \"johnwick@gmail.com\""

# Example with caching data between requests
