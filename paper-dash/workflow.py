import pandas as pd
import os
from typing import Optional, List
import logging
from paperdash import utils

def workflow_generate_draft(
    batch,
    report_name,
    dependencies,
    report_function,
    hours : int = 168,
    template_config : dict = {},
    instrutions : bool = True
) -> str:
    stage = 'draft' #Enum['draft', 'submited', 'final', 'sent']
    
    #pré-cleanup
    if os.path.exists('.report_temp'):
        os.system('rm -r .report_temp')
    if os.path.exists(report_name):
        os.system(f'rm -r {report_name}')
    if os.path.exists(f'{report_name}.zip'):
        os.system(f'rm {report_name}.zip')
    #end pré-cleanup

    report_function(
        None, 
        dependencies,
        generate_markdown=True,
        zip_temp_folder=report_name,
        generate_pdf = False,
        template_config = template_config,
        instrutions=instrutions,
    )

    assert os.path.exists(f'{report_name}.zip')
    with open(f'{report_name}.zip', 'rb') as f:
        content : bytes = f.read()

    url = utils.blob_upload_and_generate_link(
        os.getenv('BLOB_CONN_STRING'),
        container = 'reports',
        filename = f'{stage}/{batch}/{report_name}.zip',
        content = content,
        hours = hours,
    )
    assert url
    
    #pos-cleanup
    os.system(f'rm {report_name}.zip')
    #end pos-cleanup

    return url

def workflow_generate_final(
    batch : str,
    report_name : str,
    hours : int = 168,
):
    out_path = f'../reports/{report_name}.pdf'
    # Download submitted report
    if utils.blob_exists(
        os.getenv('BLOB_CONN_STRING'),
        container = 'reports',
        filename = f'submitted/{batch}/{report_name}.zip',
    ):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>', 1)
        _ = utils.blob_download(
            os.getenv('BLOB_CONN_STRING'),
            container = 'reports',
            filename = f'submitted/{batch}/{report_name}.zip',
            filename_local = f'{report_name}.zip'
        )
    elif utils.blob_exists(
        os.getenv('BLOB_CONN_STRING'),
        container = 'reports',
        filename = f'draft/{batch}/{report_name}.zip',
    ):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>', 2)
        _ = utils.blob_download(
            os.getenv('BLOB_CONN_STRING'),
            container = 'reports',
            filename = f'draft/{batch}/{report_name}.zip',
            filename_local = f'{report_name}.zip'
        )
    else:
        raise Exception(f'No report found for {report_name}')


    if os.path.exists(f'{report_name}/'):
        os.system(f'rm -r {report_name}/')
    os.system(f'mkdir {report_name} && cd {report_name} && unzip ../{report_name}.zip')
    if os.path.exists(f'.report_temp/'):
        os.system(f'rm -r .report_temp/')
    os.system(f'mv {report_name} .report_temp')

    # Remove instructions
    with open('.report_temp/report.md', 'r') as f:
        text : str = f.read()
    
    output_lines = []
    is_in_comment : bool = False
    for line in text.split('\n'):
        if '==[MANUAL]==' in line:
            is_in_comment = True
            continue
        elif '==[END OF MANUAL]==' in line:
            is_in_comment = False
            continue
        elif is_in_comment:
            continue
        else:
            output_lines.append(line)
    text = '\n'.join(output_lines)
    
    with open('.report_temp/report.md', 'w') as f:
        f.write(text)
    
    # Save 
    report = shared.StaticReport.load('.report_temp')
    report.save(
        out_path, 
        header_footer_fist = True, 
        generate_markdown = False,
        generate_pdf = True,
    )
    assert os.path.exists(out_path)
    with open(out_path, 'rb') as f:
        content : bytes = f.read()
    
    # Upload
    stage = 'final'
    url = utils.blob_upload_and_generate_link(
        os.getenv('BLOB_CONN_STRING'),
        container = 'reports',
        filename = f'{stage}/{batch}/{report_name}.pdf',
        content = content,
        hours = hours,
        overwrite=True,
    )
    
    #pos-cleanup
    os.system(f'rm {out_path}')
    #end pos-cleanup
    
    
    return url




####################
def example_report_template(
    out_path : str, 
    dependencies : dict, 
    end_date : datetime.datetime = None, 
    window_days : int = 30,
    verbosity : int=0, 
    template_config : dict = {},
    instrutions : bool = True,
    **kwargs
) -> reporting.StaticReport:
    '''
    kwargs will be passed to `save`
    '''
    connector : Connector = dependencies['connector']
    connector.load()
    customer : dict = dependencies['customer']
    dates = shared.datetime_ago(window_days = window_days, end_date = end_date)

    report = reporting.StaticReport(
        variables={
            'company': 'Skaylink CSC',
            'title': f"{customer['customerName']} - From {dates[0]} to {dates[1]}",
            'author': 'Skaylink',
            'subject': 'Security report',
            'keywords': 'security,incidents,performance',
            'date': str(datetime.datetime.now()).split('.')[0],
        },
        verbosity=verbosity
    )
    report.add_text(f"Nothing", style='title1')
    report.add_text(f"Empty")
    report.save(out_path, header_footer_fist=True, **kwargs)
    return report
