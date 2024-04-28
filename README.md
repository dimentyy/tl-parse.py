# Parsing library

### Absolute bloatware. 🚀

```python
from telethon import TelegramClient
from dimentyy.tl.parse import HTML

client: TelegramClient = ...

client.parse_mode = HTML(client)  # two ways of applying
parser = HTML.applied_to(client)  # preferred

# From now on, every message will be handled by the 
# new parser. It resembles default "HTML", but with
# some new features such as mentions and spoilers!
```

### Installation

```shell
pip install dimentyy.tl-parse
```

---

- ### Correct offset & length
Text formatting won't be offset! Using `len()` will actually result in the wrong length if the text contains some specific Unicode characters, such as some emojis.

- ### Mentions
```html
<!-- Telethon version, a little unreadable, right? -->
<a href="tg://user?id=490288812">dimentyy</a>

<!-- Uses real mention without replacing <a> when sending -->
<mention user_id=490288812>dimentyy</mention>
```

- ### Spoilers
```html
<spoiler>I will never update burger-bot</spoiler>

<!-- Consistent name -->
```
- `<custom_emoji document_id=123></custom_emoji>` _(needs testing!)_

### Features to come:
- Unparsing
- Fixing improper entities order _(testing)_
```html
<!-- Some clients will display that incorrectly, event -->
<b>BOLD. <i>BOTH.</b> ITALIC.</i> <!-- Even GitHub won't highlight </i> -->

<!-- So, this feature will fix that -->
<b>BOLD. <i>BOTH.</i></b><i> ITALIC.</i>
```

###### MIT license.
