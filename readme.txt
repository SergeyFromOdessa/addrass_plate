read
    https://cairographics.org/download/
    https://pycairo.readthedocs.io/en/latest/getting_started.html

pip install pycairo
pip install reportlab

in address_plate/fonts insert:
probanav2-bold-webfont.ttf
probanav2-regular-webfont.ttf
probanav2-semibold-webfont.ttf


commands example:

python address_plate.py vertical --type 'вулиця' --name 'Омеляновича-Павленка' --translit 'Omelyanovycha-Pavlenka vulytsia' --number '25' > Омеляновича-Павленка25.pdf
python address_plate.py --wide vertical --type 'вулиця' --name 'Омеляновича-Павленка' --translit 'Omelyanovycha-Pavlenka vulytsia' --number '25' > Омеляновича-Павленка25-w.pdf
python address_plate.py name --type 'вулиця' --name 'Хорива' --translit 'Khoryva vulytsia'  > Хорива.pdf
python address_plate.py number --number '12' --left 14 --right 12А > 12-14-12A.pdf


