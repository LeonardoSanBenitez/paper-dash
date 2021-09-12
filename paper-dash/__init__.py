import pandas as pd
import os
import matplotlib.pyplot as plt

from uuid import uuid4
from IPython.display import display, Markdown, Latex


class StaticReport():
    def __init__(self, engine:str='default', verbosity:int=1):
        self.verbosity = verbosity
        self.report = ''

        if os.path.exists(f".report_temp/"):
            os.system(f"rm -r .report_temp/")
        os.system(f"mkdir .report_temp/")
    
    def add_text(self, text:str, style:str = 'normal'):
        if style=='title1': text = '# ' + text
        if self.verbosity: display(Markdown(text))
        self.report += text + '\n'
    
    def add_graph(self, width:str='100%'):
        # Other styling options: https://stackoverflow.com/a/34894696/12555523
        id = str(uuid4())
        plt.savefig(f".report_temp/{id}.png")
        self.report += '\n\n' + f'![](.report_temp/{id}.png)' + '{width=' + width + '}' + '\\ \n\n'
    
    def add_table(self, df:pd.DataFrame):
        text = df.to_markdown()
        if self.verbosity: display(Markdown(text))
        self.report += '\n\n' + text + '\n\n'
        pass
    
    def save(self, filename:str, ):
        if filename[-3:] != 'pdf':
            raise NotImplementedError('Unsuported format')

        with open('.report_temp/report.md', 'w') as f:
            f.write(self.report)
        os.system(f"pandoc .report_temp/report.md --from markdown+pipe_tables+link_attributes --latex-engine=xelatex -o {filename}")