from datetime import date
from os import system

logo_path = "../logo.png"
dirpath = "./extensions/pdfgen/tmp/"
preamble = r"""\documentclass{article}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{hyperref}
\begin{document}
\noindent\includegraphics[width=1.5cm]{""" + logo_path + r"}\par\vspace{1cm}"


def generate_pdf_from_tex(source):
    texfilepath = "pdf.tex"
    with open(dirpath + texfilepath, "w") as f:
        f.write(source)
    system(f"(cd {dirpath} && pdflatex {texfilepath})")


def generate_thank_you_letter(key, student, programme):
    url = f"https://student.isebarn.com/application?id={key}"
    href = "\href{visir.is}{god}"
    date_ = date.today().strftime("%B %d, %Y")
    source = preamble
    source += rf"\noindent Customer Ref: {key}\par\medskip"
    source += rf"\noindent {student.get('name')}\par"
    source += rf"\noindent {student.get('address')}\par\medskip"
    source += rf"\noindent Date: {date_}" + r"\par\vspace{1cm}"
    source += rf"\noindent Dear {student.get('first_name')},\par\smallskip "
    source += rf"\noindent We are pleased to offer you a place on the program:\
         {programme.get('country')} {programme.get('description')} on the condition \
         that you submit the Student Profile completed as soon as possible.\par\smallskip "
    source += rf"\noindent Herewith, we enclose your Access Link to your \
        Student Profile forms.\par\smallskip "
    source += rf"\noindent \href{{{url}}}{{Click here to open your application}} \par\smallskip "
    source += rf"\noindent Your sincerely, into Education"
    generate_pdf_from_tex(source + "\end{document}")


def generate_acceptance_letter_and_contract(key, student, programme):
    date_ = date.today().strftime("%B %d, %Y")
    source = preamble
    source += rf"\noindent Customer Ref: {key}\par\medskip"
    source += rf"\noindent Date: {date_}" + r"\par\vspace{1cm}"
    source += rf"\noindent Dear {student.get('name', '')},\par "
    source += rf"\noindent Dear {student.get('parentsname', '')},\par\smallskip "
    source += rf"\noindent Thank you for submitting your Student Profile forms.\
        \par\smallskip\smallskip\smallskip "
    source += rf"\noindent We can now confirm your place on the program: \
        {programme.get('country')} {programme.get('description')} {programme.get('price')} \
        as soon as we receive the enclosed contract signed by you and your parents. \
        The Contract is attached to this letter.\par\smallskip\smallskip\smallskip"
    source += r"\noindent Once we receive the contract your Student Profile forms will be send to \
        our partner organisation and the search for your Host Family and school will begin. \
        As soon as we this placement infromation we shall organise your flight.\
            \par\smallskip\smallskip\smallskip "
    source += r"\noindent You will be invited to attend a PreDeparture Seminar to inform you \
        of everything you need to know for a successful exchange programme. \
        This date any location will be sent to you in good time.\
        \par\smallskip\smallskip\smallskip "
    source += r"\noindent Your sincerely, into Education"
    generate_pdf_from_tex(source + "\end{document}")


def generate_invoice(key, student, programme):
    date_ = date.today().strftime("%B %d, %Y")
    source = preamble
    source += rf"\noindent Customer Ref: {key}\par\medskip"
    source += rf"\noindent Date: {date_}" + r"\par\vspace{1cm}"
    source += rf"\noindent Dear {student.get('first_name', '')},\par "
    source += rf"\noindent Dear {student.get('parentsname', '')},\par\smallskip "
    source += rf"\noindent {student.get('address', '')}\par\bigskip"
    source += r"\begin{center}\noindent INVOICE\par\medskip\noindent\
     \begin{tabular}{ll}\textbf{Service}&\textbf{Price}\\"
    source += rf"{programme.get('code')}\ {programme.get('country')}\
     {programme.get('description')} & {programme.get('price', 0)}\\"
    source += rf"Options & {programme.get('diet', 0)}\\"
    source += rf"Extra & {programme.get('other', 0)}\\"
    total_price = programme.get('price', 0) + programme.get('diet', 0)\
     + programme.get('other', 0)
    source += rf"\hline Total & {total_price}"
    source += r"\end{tabular}\end{center}\par\bigskip "
    source += r"\noindent This invoice is payable as follows:\par "
    source += rf"\noindent {total_price * 0.3} (30\%) immediately\par "
    source += rf"\noindent {total_price * 0.3} (30\%) 1st February\par "
    source += rf"\noindent {total_price * 0.2} (20\%) 1st March\par "
    source += rf"\noindent {total_price * 0.2} (20\%) 1st May\par "
    source += r"\noindent Bank details: IBAN\par\medskip "
    source += rf"\noindent When paying please quote participant's name and Customer\
     number Ref above. Your sincerely, into Education."
    generate_pdf_from_tex(source + "\end{document}")


def generate_invitation(key, student, pds):
    date_ = date.today().strftime("%B %d, %Y")
    source = preamble
    source += rf"\noindent Customer Ref: {key}\par\medskip"
    source += rf"\noindent {student.get('name')}\par"
    source += rf"\noindent {student.get('address')}\par\medskip"
    source += rf"\noindent Date: {date_}" + r"\par\vspace{1cm}"
    source += rf"\noindent Dear {student.get('first_name')},\par\smallskip "
    source += r"\noindent We invite you to attend the obligatory PreDeparture Seminar (PDS).\par\smallskip "
    source += rf"\noindent Date and place: {pds['dates']} {pds['name']} {pds['address']}.\par\smallskip "# {pds['contact_number']}. \par\smallskip "
    source += rf"\noindent {pds['contact_number']}. \par\smallskip "
    source += rf"\noindent Time: {pds['name']} {pds['arrival_time']} finishing at {pds['name']} {pds['end_time']}\par\smallskip "
    source += rf"\noindent We look forward to welcoming you."
    generate_pdf_from_tex(source + "\end{document}")


def generate_placement(key, student, programme):
    host = student.get('host_family', {})
    school = student.get('host_school', {})
    airport = student.get('host_airport', {})
    from pprint import pprint
    pprint(school)
    date_ = date.today().strftime("%B %d, %Y")
    address = host.get('address', {})
    address = f"{address.get('line_1', '')} {address.get('city', '')}, \
        {address.get('country', '')}"
    school_address = f"{school.get('address', {}).get('line_1', '')} {school.get('address', {}).get('city', '')}, \
        {school.get('address', {}).get('country', '')}"        
    source = preamble
    from pprint import pprint
    pprint(host)
    source += rf"\noindent Customer Ref: {key}\par\medskip"
    source += rf"\noindent {student['name']}\par"
    source += rf"\noindent {student['address']}\par\medskip"
    source += rf"\noindent Date: {date_}" + r"\par\vspace{1cm}"
    source += r"\section*{Placement}"
    source += rf"\noindent Dear {student['first_name']},\par\smallskip "
    source += rf"\noindent Congratulations! You have a family in {programme['country']}! \
         We are pleased to send you your placement details.\par\smallskip "
    source += rf"\noindent You will be living with: {host.get('mother', {}).get('first_name', '')} and \
        {host.get('father', {}).get('first_name', '')},\par\smallskip "
    source += rf"\noindent {address}\par\smallskip "
    if any(host.get('child', [])):
        source += r"\noindent \subsubsection*{Children}\begin{itemize}"
        for child in host.get('child', []):
            source += rf"\item {child['name']} ({child.get('gender', 'M')})"
        source += r"\end{itemize}"
    if any(host.get('pet', [])):
        source += r"\subsubsection*{Pets}\begin{itemize}"
        for pet in host.get('pet', []):
            source += rf"\item {pet['name']}"
        source += r"\end{itemize}"
    source += r"\subsubsection*{School}"
    source += rf"\noindent {school['name']}\par\noindent {school_address}\par"
    source += r"\subsubsection*{Host Family details}"
    # source += rf"\noindent {host['details']}\par"
    #source += r"\subsubsection*{Local contact}"
    #source += rf"\noindent {coordinator['name']} {coordinator['phone']} {coordinator['email']}\par"
    source += r"\subsubsection*{Airport/station}"
    source += rf"\noindent {airport['name']}\noindent {airport['code']}\par\bigskip "
    source += rf"\noindent Please contact your host family soon to tell them a bit about yourself.\
        \par\smallskip "
    source += rf"\noindent We look forward to welcoming you.\par\smallskip"
    source += rf"\noindent Your sincerely, into Education."
    generate_pdf_from_tex(source + "\end{document}")
