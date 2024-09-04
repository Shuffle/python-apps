# Microsoft Teams App

The MS Teams app for sending an alert to Teams and allowing users to manage alert from Teams.

![alt text](https://github.com/Shuffle/python-apps/blob/master/microsoft-teams/1.0.0/MicrosoftTeams-image.png?raw=true)

## Actions

- Send simple text
- Send rich text
- Send actionable message
- Get user input

## Requirements

- Microsoft Teams account.

## Setup

1. Go to teams section in Teams app.
2. Select the team then select channel you want to send alert to. (__All the members in same channel will be able to see and react to alert/message__).
3. Go to connectors &#8594; incoming webhook select configure.
4. Provide suitable name & picture (optional).
5. Copy webhook url and head over to shuffle.
6. Add Teams app in your workflow, use webhook url in app.

## Note
- If you are planning on sending actionable message or get user input, you'll need to have webhook running in your workflow (Go to your workflow &#8594; Triggers select webhook and start it).
- Once you start webhook you'll see webhook url. Copy & use the same in callback_url for actionable message / user input.
- Read more about webhook [here](https://shuffler.io/docs/triggers#webhook).
