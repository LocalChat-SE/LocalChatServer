import json

api_string = '''
{
  "chats": [
      {
        "lat": 253.12,
        "lon": 4822,
        "name": "myChat",
        "enrolled": [
            {
              "username": "Tayfun",
              "isBanned": true
            },
            {
              "username": "Shoe",
              "isBanned": true
            }
          ]
      },
      {
        "lat": 2.12,
        "lon": 4,
        "name": "myChat2",
        "enrolled": [
            {
              "username": "Jessica",
              "isBanned": false
            }
          ]
      }
    ]
}'''

parsed = json.loads(api_string)
for chat in parsed['chats']:
    print(chat['enrolled'][0])
