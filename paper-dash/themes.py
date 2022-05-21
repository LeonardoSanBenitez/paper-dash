# https://learnbyexample.github.io/customizing-pandoc/#pdf-properties
# and his repo, https://github.com/learnbyexample/learnbyexample.github.io/tree/master/files/pandoc_pdf
# Other good style, to html: https://gist.github.com/killercup/5917178
# pandoc variables: https://pandoc.org/MANUAL.html#variables-for-latex
# several stylizations: https://jdhao.github.io/2019/05/30/markdown2pdf_pandoc/
theme_default = {
    'required_variables': [
        'company', 
        'title',
        'author',
        'subject',
        'keywords',
        'date',
    ],
    'images': {},
    'files': {
        '''basic_headers.tex''': r'''
            \usepackage{float}
            \usepackage[
                a4paper,
                top=0.5cm,
                bottom=0.5cm,
                right=2cm,
                left=2cm,
                headheight=1.5cm,
                includeheadfoot
            ]{geometry}
        ''',
        'header_footer.tex': r'''
            \usepackage{graphicx}
            \usepackage{fancyhdr}
            \pagestyle{fancy}

            \lhead{$title$}
            \rhead{Generated at $date$}

            %\cfoot{$company$}
            \cfoot{\includegraphics[height=1cm]{logo.jpg}}
            \renewcommand{\headrulewidth}{2pt}

            \rfoot{\thepage}
            \renewcommand{\footrulewidth}{1pt}
            
            %\lhead{}
            %\chead{}
            %\rhead{}
            
            %\lfoot{}
            %\cfoot{}
            %\rfoot{}
            
            %\thepage
            %\thechapter
            %\thesection
            %\chaptername
        ''',
        'header_footer_no_first.tex': r'''
            \thispagestyle{empty}
        ''',
        'bullet_style.tex': r'''
            % https://stackoverflow.com/questions/22156999/how-to-change-the-style-of-bullets-in-pandoc-markdown

            \usepackage{enumitem}
            \usepackage{amsfonts}

            \setlist[itemize,1]{label=$\bullet$}
            \setlist[itemize,2]{label=$\circ$}
            \setlist[itemize,3]{label=$\star$}

            %% \setlist[itemize,2]{label=$\diamond$}
            %% \setlist[itemize,1]{label=$\star$}
            %% \setlist[itemize,1]{label=$\bullet$}
            %% \setlist[itemize,1]{label=$\checkmark$}
        ''',
        'chapter_break.tex': r'''
            %% Adds pagebreak between chapters
            % from comments of accepted answer
            % https://superuser.com/questions/601469/getting-chapters-to-start-on-a-new-page-in-a-pandoc-generated-pdf
            \usepackage{sectsty}
            \sectionfont{\clearpage\underline\LARGE}

            % accepted answer gave error
            %\usepackage{titlesec}
            %\newcommand{\sectionbreak}{\clearpage}
        ''',
        'inline_code.tex': r'''
            %% https://stackoverflow.com/questions/40975004/pandoc-latex-change-backtick-highlight
            \usepackage{fancyvrb,newverbs,xcolor}

            %\definecolor{Light}{gray}{.90}
            %% https://martin-thoma.com/colors-in-latex/
            %% https://en.wikibooks.org/wiki/LaTeX/Colors
            \definecolor{Light}{HTML}{F4F4F4}

            \let\oldtexttt\texttt
            \renewcommand{\texttt}[1]{
                \colorbox{Light}{\oldtexttt{#1}}
            }
        ''',
        'pdf_properties.tex': r'''
            % https://tex.stackexchange.com/questions/23235/eliminate-edit-pdf-properties-added-by-pdflatex
            \usepackage{hyperref}

            \hypersetup{
            pdftitle={$title$},
            pdfauthor={$author$},
            pdfsubject={$subject$},
            pdfkeywords={$keywords$}
            }
        ''',
        'cover.tex': r'''
            \includegraphics{cover.png}
            \thispagestyle{empty}
        ''',
        'quote.tex': r'''
            \usepackage{tcolorbox}
            \newtcolorbox{myquote}{colback=red!5!white, colframe=red!75!black}
            \renewenvironment{quote}{\begin{myquote}}{\end{myquote}}
        ''',
        'pygments.theme': r'''
            {
                "text-color": null,
                "background-color": "#f8f8f8",
                "line-number-color": "#aaaaaa",
                "line-number-background-color": null,
                "text-styles": {
                    "Other": {
                        "text-color": "#007020",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Attribute": {
                        "text-color": "#7d9029",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "SpecialString": {
                        "text-color": "#bb6688",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Annotation": {
                        "text-color": "#60a0b0",
                        "background-color": null,
                        "bold": true,
                        "italic": true,
                        "underline": false
                    },
                    "Function": {
                        "text-color": "#06287e",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "String": {
                        "text-color": "#4070a0",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "ControlFlow": {
                        "text-color": "#007020",
                        "background-color": null,
                        "bold": true,
                        "italic": false,
                        "underline": false
                    },
                    "Operator": {
                        "text-color": "#666666",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Error": {
                        "text-color": "#ff0000",
                        "background-color": null,
                        "bold": true,
                        "italic": false,
                        "underline": false
                    },
                    "BaseN": {
                        "text-color": "#40a070",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Alert": {
                        "text-color": "#ff0000",
                        "background-color": null,
                        "bold": true,
                        "italic": false,
                        "underline": false
                    },
                    "Variable": {
                        "text-color": "#19177c",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "BuiltIn": {
                        "text-color": null,
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Extension": {
                        "text-color": null,
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Preprocessor": {
                        "text-color": "#bc7a00",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Information": {
                        "text-color": "#60a0b0",
                        "background-color": null,
                        "bold": true,
                        "italic": true,
                        "underline": false
                    },
                    "VerbatimString": {
                        "text-color": "#4070a0",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Warning": {
                        "text-color": "#60a0b0",
                        "background-color": null,
                        "bold": true,
                        "italic": true,
                        "underline": false
                    },
                    "Documentation": {
                        "text-color": "#ba2121",
                        "background-color": null,
                        "bold": false,
                        "italic": true,
                        "underline": false
                    },
                    "Import": {
                        "text-color": null,
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Char": {
                        "text-color": "#4070a0",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "DataType": {
                        "text-color": "#902000",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Float": {
                        "text-color": "#40a070",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Comment": {
                        "text-color": "#9c9c9c",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "CommentVar": {
                        "text-color": "#60a0b0",
                        "background-color": null,
                        "bold": true,
                        "italic": true,
                        "underline": false
                    },
                    "Constant": {
                        "text-color": "#880000",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "SpecialChar": {
                        "text-color": "#4070a0",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "DecVal": {
                        "text-color": "#40a070",
                        "background-color": null,
                        "bold": false,
                        "italic": false,
                        "underline": false
                    },
                    "Keyword": {
                        "text-color": "#007020",
                        "background-color": null,
                        "bold": true,
                        "italic": false,
                        "underline": false
                    }
                }
            }
        '''
    },
    'tex_headers': [
        'basic_headers.tex',
        'bullet_style.tex',
        'chapter_break.tex',
        'inline_code.tex',
        'pdf_properties.tex',
        'quote.tex',
    ],
}
