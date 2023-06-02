# Chatsum

Chatsum is a bot helps summarizing information from all your group chats.
Every day for each group It will generate reports like:

```
2023-06-01 09:30:28 Popularity:10 Mood:😃  
【Planning a surprise birthday party for John next week.】
Alice: Let's have a surprise party for John's birthday next week. We can have it at my place and get a cake. 
Bob: Great idea! I can invite some of his other friends. We should plan some games and decorate the place.
Carol: Sounds fun, I'll bring some snacks and drinks. Let's keep this a secret from John.

2023-06-01 11:04:23 Popularity:7 Mood:😊
【Discussing birthday gift ideas for John.】
Alice: Any ideas for gifts for John? He's into photography, maybe a new lens?
Bob: A lens is a great idea! I can chip in for that. Or maybe a photo album or framed prints of his favorite photos.
Carol: Those are lovely thoughtful gifts! I was thinking of getting him a nice watch. We can all sign a birthday card too.

2023-06-01 12:22:01 Popularity:5 Mood:😕  
【Debating whether to invite John's ex-girlfriend to the party.】 
Alice: Should we invite John's ex Lucy to the party? They're still friends but it may be awkward.
Bob: I don't think we should. They only recently broke up and it may make John uncomfortable. 
Carol: I agree, let's not invite Lucy. We want John to enjoy himself at the party.
```

Currently Chatsum only supports receiving chat records from wechat.


## How to Use

Python version should >= 3.7 <= 3.10

1. clone the project and `cd` into project folder.

2. install python requirements:
```bash
pip install -r requirements.txt
```

3. `cd` into `run` folder. It's the folder to start the app and store runtime data.
```bash
cd run
```

4. create a startup script by copying `sample.start.sh` and make some configs in it.
```bash
cp sample.start.sh start.sh
vim start.sh
```

5. set clickhouse password and wechaty configs in the `start.sh`
```bash
# clickhouse is used to store your chat history
# choose a strong password to protect it
export CLICKHOUSE_USER="myuser"
export CLICKHOUSE_PASSWORD="mypassword"

# For personal wechat user, there're 2 options for WECHATY_PUPPET
# "wechaty-puppet-wechat" uses web login, which is free but unstable and your
#     account has a high risk of being blocked by tencent
# "wechaty-puppet-padlocal" is more stable and according to wechaty team is less
#     likely to get your account blocked
export WECHATY_PUPPET="wechaty-puppet-padlocal"
# padlocal token is required if using "wechaty-puppet-padlocal"
# get token from http://pad-local.com/
export WECHATY_PUPPET_PADLOCAL_TOKEN="puppet_padlocal_"
export WECHATY_PUPPET_SERVER_PORT=8888
# WECHATY_TOKEN should be set to your own secret token
export WECHATY_TOKEN="mywechatytoken"
```

6. execute the startup script
```bash
bash start.sh
```
