import pdfkit


class SudokuPrinter:
    """prints sudokus to pdf
    """
    def __init__(self, sudokus):
        """
        :param sudokus: list of sudoku 9x9 arrays
        """
        self.number_of_sudokus = len(sudokus)
        self.sudokus = sudokus
        self.document = ""

    def print_pdf(self, pdf_path="sudoku.pdf"):
        self.add_document_header()
        self.add_sudokus()
        self.add_document_footer()
        self.make_pdf(pdf_path)

    def add_document_header(self):
        self.document += """<!DOCTYPE html>
        <html>
            <head>
                <link rel=\"stylesheet\" href=\"style.css\">
            </head>
        <body>
            <div class=\"content\">"""

    def add_sudokus(self):
        for sudoku in self.sudokus:
            self.add_sudoku_board(sudoku)

    def add_sudoku_board(self, sudoku):
        self.document += "<table>\n"
        for i in range(9):
            self.document += "<tr>\n"
            for j in range(9):
                self.document += "<td class=\"cell row{} col{}\">".format(i, j)
                self.document += str(sudoku[i, j]) if sudoku[i, j] > 0 else "&nbsp;"
                self.document += "</td>\n"
            self.document += "</tr>\n"
        self.document += "</table>\n"

    def add_document_footer(self):
        self.document += "</div>\n</body>\n</html>"

    def make_pdf(self, pdf_path):
        options = {
            'quiet': '',
            'disable-smart-shrinking': None,
            'page-size': 'A4',
            'margin-top': '0.0cm',
            'margin-right': '0.0cm',
            'margin-bottom': '0.0cm',
            'margin-left': '0.0cm',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdfkit.from_string(self.document, pdf_path, options=options,
                           css="style.css")
