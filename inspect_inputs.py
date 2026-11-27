"""读取本地资料目录并报告文件版本指纹。"""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path


def inventory(directory):
    for path in sorted(directory.rglob('*')):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        content = raw.decode('utf-8')
        if path.suffix == '.json':
            json.loads(content)
        elif path.suffix == '.jsonl':
            for number, line in enumerate(content.splitlines(), 1):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as error:
                        raise ValueError(f'{path}:{number}: JSONL 无效') from error
        yield dict(path=path.relative_to(directory).as_posix(), size=len(raw), sha256=sha256(raw).hexdigest())


if __name__ == '__main__':
    parser = ArgumentParser(description='检查文本、JSON 与 JSONL 资料，列出文件及原始字节摘要。')
    parser.add_argument('directory', type=Path, help='资料目录')
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error('资料目录不存在')
    result = list(inventory(args.directory))
    if not result:
        parser.error('资料目录为空')
    print(json.dumps(result, ensure_ascii=False, indent=2))
