# rat-janty

Il est gentil

```bash
pyinstaller server.py # create .exe from py --> dist/server.exe

pyinstaller --onefile --windowed --icon="../assets/chilli.ico" --specpath="./spec" --name="rat-gentil" src/client.py
pyinstaller --onefile --windowed --icon="../assets/chilli.ico" --specpath="./spec" src/server.py
```

```bash
.\signtool sign /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 "C:\Users\julie\Desktop\VM shared\cible\rat-gentil.exe"
```