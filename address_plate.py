from argparse import ArgumentParser
from address_plate.pdf_maker import street_name_pdf, house_number_pdf, vertical_pdf
import sys


def street_name(args):
    pdf, file_name = street_name_pdf(street_type=args.type, street_name=args.name,
                                     street_translit=args.translit,
                                     wide='wide' if args.wide else 'thin')
    sys.stdout = sys.stdout.detach()
    sys.stdout.write(pdf.read())


def house_number(args):
    pdf, file_name = house_number_pdf(house_num=args.number, left_num=args.left, right_num=args.right,
                                      wide='wide' if args.wide else 'thin')
    sys.stdout = sys.stdout.detach()
    sys.stdout.write(pdf.read())


def vertical(args):
    pdf, file_name = vertical_pdf(street_type=args.type, street_name=args.name,
                                  street_translit=args.translit, house_num=args.number,
                                  wide='wide' if args.wide else 'thin')
    sys.stdout = sys.stdout.detach()
    sys.stdout.write(pdf.read())


def main():
    parser = ArgumentParser()

    parser.add_argument('--wide', help='Wide', action='store_true')

    sub_parser = parser.add_subparsers(title='Address plate', description='Address plate description')

    street_name_parser = sub_parser.add_parser('name', help='Street name')
    street_name_parser.add_argument('--type', help='Street type', type=str, required=True)
    street_name_parser.add_argument('--name', help='Street name', type=str, required=True)
    street_name_parser.add_argument('--translit', help='Street translit', type=str, required=True)
    street_name_parser.set_defaults(func=street_name)

    street_number_parser = sub_parser.add_parser('number', help='House number')
    street_number_parser.add_argument('--number', help='House number', type=str, required=True)
    street_number_parser.add_argument('--left', help='Left arrow', type=str)
    street_number_parser.add_argument('--right', help='Right arrow', type=str)
    street_number_parser.set_defaults(func=house_number)

    vertical_parser = sub_parser.add_parser('vertical', help='Vertical')
    vertical_parser.add_argument('--type', help='Street type', type=str, required=True)
    vertical_parser.add_argument('--name', help='Street name', type=str, required=True)
    vertical_parser.add_argument('--translit', help='Street translit', type=str, required=True)
    vertical_parser.add_argument('--number', help='House number', type=str, required=True)
    vertical_parser.set_defaults(func=vertical)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

# python address_plate.py --wide vertical --type 'улица' --name 'street name' --translit translit --number '25/3А' > test.pdf
# python address_plate.py name --type 'проспект' --name 'Название узкой улицы' --translit translit  > test.pdf
# python address_plate.py number --number '25/3А' --left 23А > test.pdf

# python address_plate.py vertical --type 'вулиця' --name 'Омеляновича-Павленка' --translit 'Omelyanovycha-Pavlenka vulytsia' --number '25' > Омеляновича-Павленка25.pdf
# python address_plate.py name --type 'вулиця' --name 'Хорива' --translit 'Khoryva vulytsia'  > Хорива.pdf
# python address_plate.py number --number '12' --left 14 --right 12А > 12-14-12A.pdf

