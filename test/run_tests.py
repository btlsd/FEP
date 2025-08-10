import subprocess
import datetime
import os


def run_command(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr


def main():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
    os.makedirs('test', exist_ok=True)
    log_path = os.path.join('test', f'{timestamp}_{version}.txt')

    outputs = []
    outputs.append(f'Version: {version}\nTime: {timestamp}\n')
    outputs.append('## py_compile\n')
    outputs.append(run_command("python -m py_compile $(git ls-files '*.py')"))
    outputs.append('\n## unittest\n')
    outputs.append(run_command('python -m unittest discover -v'))

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(outputs))
    print(f'log saved to {log_path}')


if __name__ == '__main__':
    main()
