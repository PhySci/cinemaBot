python -m virtualenv --no-site-packages env
CALL .\env\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m ipykernel install --user --name=TagsEmbeddings
CALL .\env\Scripts\deactivate.bat
