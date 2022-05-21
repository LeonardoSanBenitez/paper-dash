from __future__ import annotations
import pandas as pd
import os
import matplotlib.pyplot as plt
from plotly.graph_objs._figure import Figure
from uuid import uuid4
import base64
from typing import Optional
import json
from shared.reporting.themes import theme_csc as theme

__version__ = '0.1.6'

class StaticReport():
    def __init__(self, variables:dict={}, engine:str='default', verbosity:int=0):
        self.variables = variables
        self.verbosity = verbosity
        self.engine = engine
        self.report = ''

        #if os.path.exists(f".report_temp/"):
        #    os.system(f"rm -r .report_temp/")
        if not os.path.exists(f".report_temp/"):
            os.system(f"mkdir .report_temp/")
        
    @classmethod
    def load(cls, path : str) -> StaticReport:
        with open(f'{path}/config.json', 'r') as f:
            config = json.loads(f.read())
        report = StaticReport(
            variables = config['variables'], 
            engine = config['engine'], 
            verbosity = config['verbosity'],
        )
        return report 
    
    def add_text(self, text:str, style:str = 'normal'):
        if style=='title1': text = '# ' + text
        elif style=='title2': text = '## ' + text
        elif style=='normal': text = text + '\n'
        else:
            raise NotImplementedError('Unsupported style')

        #if self.verbosity: display(Markdown(text))
        self.report += text + '\n'
    
    def add_graph(self, width:str='100%', plotly_figure: Optional[Figure] = None):
        # Other styling options: https://stackoverflow.com/a/34894696/12555523
        id = str(uuid4())
        if plotly_figure:
            plotly_figure.write_image(f".report_temp/{id}.png")
        else:
            plt.savefig(f".report_temp/{id}.png")
        self.report += '\n\n' + f'![]({id}.png)' + '{width=' + width + '}' + '\\ \n\n'
    
    def add_table(self, df:pd.DataFrame, index:bool=False):
        text = df.to_markdown(index=index)
        #if self.verbosity: display(Markdown(text))
        self.report += '\n\n' + text + '\n\n'

    def generate_pdf(
        self,
        filename : str, 
        toc : bool = False, 
        cover : bool = False, 
        header_footer : bool=True, 
        header_footer_fist : bool=False, 
        chapter_break : bool=False, 
    ):
        if os.path.exists(f'.report_temp/{filename}'):
            os.system(f'''rm .report_temp/{filename}''')
        command = f'''
        cd .report_temp/ && \
        pandoc \
        report.md \
        --from markdown+pipe_tables+link_attributes+yaml_metadata_block \
        --pdf-engine=xelatex \
        --highlight-style pygments.theme \
        --include-in-header basic_headers.tex \
        -V linkcolor:blue \
        -V mainfont="DejaVu Sans" \
        -V monofont="DejaVu Sans Mono" '''
        for header_name in theme['tex_headers']:
            command += f' --include-in-header {header_name} '
        if header_footer:
            command += '--include-in-header header_footer.tex '
        if header_footer_fist==False:
            command += '--include-before-body header_footer_no_first.tex '
        if chapter_break:
            command += '--include-in-header chapter_break.tex '
        if toc:
            command += '''
                --toc \
                -V toc-title='Table of contents' \
            '''
        if cover:
            # requires image
            # may interfere with header_footer_fist
            command += '--include-before-body cover.tex '
            raise NotImplementedError() 
        command += f'-o ../{filename}'
        print(command)
        os.system(command)

    def save(
            self, 
            filename : Optional[str] = None, 
            toc : bool = False, 
            cover : bool = False, 
            header_footer : bool = True, 
            header_footer_fist : bool = False, 
            chapter_break : bool = False, 
            return_bytes : bool = False,
            generate_markdown : bool = True,
            clean_temp_folder : bool = False,
            zip_temp_folder : Optional[str] = None,
            generate_pdf : bool = True,
        ) -> Optional[bytes]:
        # TODO: maybe this function should be refactored to something like "compile()"
        #TODO: filename can't contain spaces
        #TODO: refactor to use only python dependencies
        #TODO: chose a better font
        #TODO: do a `cd` into report_temp, so we can open the markdown and see the images
        #TODO: separe the style logic from the export logic
        if not os.path.exists(f".report_temp/"):
            os.system(f"mkdir .report_temp/")

        if not filename:
            filename = str(uuid4()) + '.pdf'
            return_bytes = True
        if filename[-3:] != 'pdf':
            raise NotImplementedError('Unsuported format')

        # Prepare files to be converted
        for style_filename in theme['files']:
            with open(f'.report_temp/{style_filename}', 'w') as f:
                text = theme['files'][style_filename]
                for v in self.variables:
                    text = text.replace('$' + v + '$', self.variables[v])
                f.write(text)
        for image_filename in theme['images']:
            # TODO:
            # this was a quick and dirty solution to include images in the header
            # Maybe a better solution is to have the images stored in azure storage, 
            # or receive the images in the report creation
            with open(f'.report_temp/{image_filename}', 'wb') as f:
                f.write(base64.b64decode(theme['images'][image_filename]))

        with open('./.report_temp/config.json', 'w') as f:
            f.write(json.dumps({
                'engine': self.engine,
                'variables': self.variables,
                'verbosity': self.verbosity,
            }))

        if generate_markdown:
            with open('.report_temp/report.md', 'wb') as f:
                f.write(self.report.encode('utf-8'))
        elif not os.path.exists('.report_temp/report.md'):
            raise ValueError('Markdown file should already exist if you do not want to generate it')

        if generate_pdf:
            self.generate_pdf(filename, toc, cover, header_footer, header_footer_fist, chapter_break)

        if zip_temp_folder:
            os.system(f'chmod 777 -R .report_temp/')
            os.system(f'cp -r .report_temp {zip_temp_folder}')
            os.system(f'cd {zip_temp_folder} && zip -r {zip_temp_folder}.zip . && cd .. && cp {zip_temp_folder}/{zip_temp_folder}.zip {zip_temp_folder}.zip')

        if return_bytes and generate_pdf:
            with open(f'.report_temp/{filename}', 'rb') as f:
                response = f.read()
        elif return_bytes and zip_temp_folder:
            with open(f'{zip_temp_folder}.zip', 'rb') as f:
                response = f.read()
        elif return_bytes:
            raise ValueError('Nothing to return')
        else:
            response = None

        if clean_temp_folder:
            os.system(f"rm -r .report_temp/")

        return response
