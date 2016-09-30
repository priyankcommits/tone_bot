# tone_bot

What is does?

Analyzes the chat and returns the social, language and emotional tone of chat to the user.
Currently supports two modes: History(previous messages) and Analyze(current message)
  Usage: /tone history [social/language/emotion]
         /tone analyze [social/language/emotion] <text>

How it does?

The bot talks to IBM Watson's ToneAnalyzer API to get the results.

Who is it for?

For sales reps using Slack, where communication effecieny is a crucial factor, this bot can help them communicate better in a positive way, helping them to track their tone.

What it can do in the future?

It can remove the negative tone causing words and replace them with positive tone words.
History: Messages will be read using time stamps, since when the user last used it till present, rather than the current fixed number of messages.

How to run?

Slash command and Watson API keys are hard coded in the lambda function, you will need to change the OAuth Token in the file before executing it.
You will need to create a Slash command in Slack and hook it to the lambda API endpoint.


Requirements for running the app are present in the requirements.txt file.


Please feel free to contact me for any doubts on running or testing.
