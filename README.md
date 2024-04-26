# README

```python
from telethon import TelegramClient
from dimentyy.tl.parse import BetterParsing

client: TelegramClient = ...
client.parse_mode = BetterParsing.HTML()

# From now on, every message will be handled by the 
# new parser. It resembles default "HTML", but with
# some new features such as mentions and spoilers!
```

###### __MIT license.__
