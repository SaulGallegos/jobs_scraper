def insert_log(job_log_info):
    with open('logs.csv', 'a') as file:
        file.write(
            f'{job_log_info["id"]}, {job_log_info["platform"]}, {job_log_info["date"]}, {job_log_info["txt_path"]}, {job_log_info["html_path"]}, {job_log_info["pdf_path"]}\n')


def is_job_in_log(job_id):
    with open('logs.csv', 'r') as file:
        for line in file:
            if job_id in line:
                return True
    return False
