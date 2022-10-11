import requests
import webvtt
import json

file = 'test/socs-career-onestop.json'
socs = json.load(open(file))
newdict = {item[0]: item[1]['description'] for item in socs.items()}
json.dump(newdict, open('test/description.json', 'w'), indent=2)

socs = json.load(open('test/description.json'))
vtt = {}
for soc in socs.keys():
    url = f'https://cdn.careeronestop.org/CaptionFiles/{soc[:2]}-{soc[-4:]}.00.vtt'
    page = requests.get(url)
    def remove_non_ascii(s):
        return "".join(c for c in s if ord(c)<128)
    content = [remove_non_ascii(line) for line in page.text.split('\r\n') if (len(line) != 0) & ~any(char.isdigit() for char in line)]
    print(soc)
    open(f'test/vtt/{soc}.txt', 'w').write(" ".join(content[1:]))
    vtt[soc] = " ".join(content[1:])
json.dump(vtt, open('test/subtitles.json', 'w'), indent=2)
