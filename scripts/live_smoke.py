"""Opt-in serial Wikipedia checks, with a persistent maximum of 30 HTTP calls."""
import argparse
import json
from pathlib import Path
import time
import wikipedia
from wikipedia import wikipedia as wiki


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budget-file', type=Path, default=Path('build/live-budget.json'))
    parser.add_argument('--report', type=Path, default=Path('build/live-report.json'))
    args = parser.parse_args()
    args.budget_file.parent.mkdir(parents=True, exist_ok=True)
    budget = json.loads(args.budget_file.read_text()) if args.budget_file.exists() else {'calls': []}
    original = wiki._SESSION.get
    report = {'checks': [], 'failures': []}

    def counted(url, **kwargs):
        if len(budget['calls']) >= 30:
            raise RuntimeError('Live request budget exhausted (30)')
        budget['calls'].append({'url': url, 'params': kwargs.get('params'), 'at': time.time()})
        args.budget_file.write_text(json.dumps(budget, ensure_ascii=False, indent=2) + '\n')
        return original(url, **kwargs)

    wiki._SESSION.get = counted
    wikipedia.set_user_agent('Wikipedia-stabilization/1.5.0 (https://github.com/goldsmith/Wikipedia)')
    wikipedia.set_rate_limiting(True)
    try:
        for language, title in [('en', 'Earth'), ('fr', 'Terre'), ('ja', '地球')]:
            try:
                wikipedia.set_lang(language)
                assert title in wikipedia.search(title, results=3)
                page = wikipedia.page(title, auto_suggest=False)
                assert page.title and page.url.startswith('https://')
                assert isinstance(page.summary, str) and page.summary
                assert isinstance(page.content, str) and page.content
                assert isinstance(page.revision_id, int)
                assert isinstance(page.sections, list) and page.sections
                assert isinstance(page.html(), str) and '<' in page.html()
                assert page.coordinates is None or len(page.coordinates) == 2
                report['checks'].append({'language': language, 'title': page.title, 'status': 'passed'})
            except Exception as exc:
                report['failures'].append({'language': language, 'error': type(exc).__name__, 'detail': str(exc)})
        try:
            wikipedia.set_lang('en')
            page = wikipedia.page('Celtuce', auto_suggest=False)
            for prop in ('images', 'links', 'references', 'categories'):
                assert isinstance(getattr(page, prop), list)
            report['checks'].append({'title': 'Celtuce', 'status': 'passed', 'properties': ['images', 'links', 'references', 'categories']})
        except Exception as exc:
            report['failures'].append({'title': 'Celtuce', 'error': type(exc).__name__, 'detail': str(exc)})
        try:
            wikipedia.page('Mercury', auto_suggest=False)
            raise AssertionError('Expected a disambiguation page')
        except wikipedia.DisambiguationError as exc:
            assert 'Mercury (planet)' in exc.options
            report['checks'].append({'title': 'Mercury', 'status': 'passed', 'options': len(exc.options)})
        except Exception as exc:
            report['failures'].append({'title': 'Mercury', 'error': type(exc).__name__, 'detail': str(exc)})
    finally:
        wiki._SESSION.get = original
        report['http_calls'] = len(budget['calls'])
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(report['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
