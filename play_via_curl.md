# Play tic-tac-toe through curl

## Create a new game

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/games' \
  -H 'accept: application/json' \
  -d ''
```
```json
{
  "game_id": "ccac4a48-afb8-42c9-8550-d0db110e5000",
  "player_id": "8f8fdbfb-45bb-4089-add6-07b1e3414b60",
  "board": [
    [
      null,
      null,
      null
    ],
    [
      null,
      null,
      null
    ],
    [
      null,
      null,
      null
    ]
  ],
  "current_turn": "X",
  "status": "waiting",
  "winner": null,
  "player_count": 1
}
```

## 2nd player joins the game
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/games/ccac4a48-afb8-42c9-8550-d0db110e5000/join' \
  -H 'accept: application/json' \
  -d ''
```
```json
{
  "game_id": "ccac4a48-afb8-42c9-8550-d0db110e5000",
  "player_id": "01176e33-298c-461e-9fdf-de3911b81e53",
  "board": [
    [
      null,
      null,
      null
    ],
    [
      null,
      null,
      null
    ],
    [
      null,
      null,
      null
    ]
  ],
  "current_turn": "X",
  "status": "in_progress",
  "winner": null,
  "player_count": 2
}
```

## 1st player makes a move
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/games/ccac4a48-afb8-42c9-8550-d0db110e5000/move' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "player_id": "8f8fdbfb-45bb-4089-add6-07b1e3414b60",
  "position": [
    1,1
  ]
}'
```
```json
{
  "game_id": "ccac4a48-afb8-42c9-8550-d0db110e5000",
  "player_id": null,
  "board": [
    [
      null,
      null,
      null
    ],
    [
      null,
      "X",
      null
    ],
    [
      null,
      null,
      null
    ]
  ],
  "current_turn": "O",
  "status": "in_progress",
  "winner": null,
  "player_count": 2
}
```

## Getting the game state
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/games/ccac4a48-afb8-42c9-8550-d0db110e5000' \
  -H 'accept: application/json'
```
```json
{
  "game_id": "ccac4a48-afb8-42c9-8550-d0db110e5000",
  "player_id": null,
  "board": [
    [
      null,
      null,
      null
    ],
```json
{
  "game_id": "ccac4a48-afb8-42c9-8550-d0db110e5000",
  "player_id": "8f8fdbfb-45bb-4089-add6-07b1e3414b60",
  "board": [
    [
      null,
      null,
      null
    ],
    [
      null,
      "X",
      null
    ],
    [
      null,
      null,
      null
    ]
  ],
  "current_turn": "O",
  "status": "in_progress",
  "winner": null,
  "player_count": 2
}
```