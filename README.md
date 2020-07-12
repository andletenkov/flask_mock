# mock-server

# Requirements
Docker need to be installed

# How to
1. Deploy service to host (or run it locally)
2. Implement custom JSON schema, put it to /schemas directory (or use "example.json" for test)
3. Execute GET {host:port}/example/users/666
4. Obtain response: "\"id\": 666, \"name\": \"John Wick\", \"email\": \"johnwick@gmail.com\""

# Example with caching data between requests
It's possible to share data between Flask request contexts via Redis cache if request have same `key`
1. Execute POST {host:port}/cache/users with some json body: f.e., {"email": "rickastley@gmail.com"}
2. Obtain response "\"id\": 123, \"status\": \"ok\""
3. Execute GET {host:port}/cache/users/123
4. Obtain response "\"id\": 123, \"email\": \"rickastley@gmail.com\""

So `email`parameter value was shared between two unrelated Flask contexts
