"""パラメータ処理ユーティリティモジュール"""

from typing import List, Optional
import click


class PrefixChoice(click.Choice):
    """前方一致による選択肢処理クラス"""
    
    def __init__(self, choices: List[str], case_sensitive: bool = False):
        super().__init__(choices, case_sensitive)
        self.choices_map = {choice.lower(): choice for choice in choices}
    
    def convert(self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> str:
        """値を変換する"""
        if not self.case_sensitive:
            value = value.lower()
            
        # 完全一致をチェック
        if value in self.choices:
            return value
            
        # 前方一致をチェック
        matched_choices = [
            choice for choice in self.choices
            if choice.lower().startswith(value.lower())
        ]
        
        if len(matched_choices) == 1:
            return matched_choices[0]
        elif len(matched_choices) > 1:
            self.fail(f"'{value}' は複数の選択肢と一致します: {', '.join(matched_choices)}", param, ctx)
        else:
            self.fail(f"'{value}' は有効な選択肢ではありません。選択肢: {', '.join(self.choices)}", param, ctx)