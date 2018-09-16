# u2b-cli
Up2Box Python CLI to automate the download

## NOTE
This is this still very rough around the edges!
PR, Bug Report, Feature Request are welcome!

### TODO
- Cleanup
- A Debug mode
- Some logging
- A requirement file (depends only on python-requests for now)
- Still need some love and testing :)

## Documentation
The code is already commented, feel free to read it!
The script will expect a `.u2b.ini` file un your home directory!

Content of the ini file:
```
[DEFAULT]
TOKEN = #Your TOKEN, available from your U2B Account
API_BASE = https://uptobox.com/api # The API URL
DL_FOLDER = #The default folder to download the file in. Can be overrided on the command line
```
