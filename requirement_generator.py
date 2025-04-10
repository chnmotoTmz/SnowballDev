import os
import json
import logging
import datetime
import difflib
from typing import Dict, Any, List, Optional

from rag_engine import RAGEngine

class RequirementGenerator:
    """
    要件定義生成器
    自然言語の要求から構造化された要件を生成する
    """
    
    def __init__(self, rag_engine: RAGEngine, output_dir: str = "./requirements"):
        """
        要件定義生成器の初期化
        
        Args:
            rag_engine: RAGエンジンのインスタンス
            output_dir: 出力ディレクトリのパス
        """
        self.rag_engine = rag_engine
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 過去の要件履歴の保存先
        self.history_dir = os.path.join(output_dir, "history")
        os.makedirs(self.history_dir, exist_ok=True)
        
        self.logger = logging.getLogger("RequirementGenerator")
    
    def analyze_requirements(self,
                           natural_language_input: str,
                           project_name: str,
                           project_type: str = "web_app") -> Dict[str, Any]:
        """
        自然言語入力から要件を分析・構造化
        
        Args:
            natural_language_input: 自然言語による要求
            project_name: プロジェクト名
            project_type: プロジェクトタイプ
            
        Returns:
            構造化された要件辞書
        """
        self.logger.info(f"プロジェクト '{project_name}' の要件分析を開始...")
        
        # RAGエンジンを使用して類似プロジェクトを検索
        self.logger.info("類似プロジェクトを検索中...")
        similar_projects = self.rag_engine.search(
            query=f"プロジェクトタイプ: {project_type}, 説明: {natural_language_input}",
            top_k=3,
            filter_criteria={"type": "requirements"}
        )
        
        # 類似プロジェクトの情報をコンテキストとして利用
        context = ""
        if similar_projects:
            self.logger.info(f"{len(similar_projects)}件の類似プロジェクトが見つかりました")
            for i, project in enumerate(similar_projects):
                context += f"\n--- 類似プロジェクト {i+1} ---\n"
                context += project["content"]
        else:
            self.logger.info("類似プロジェクトは見つかりませんでした")
        
        # 要件のスケルトンを定義
        requirements = {
            "project_name": project_name,
            "project_type": project_type,
            "creation_date": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "natural_language_input": natural_language_input,
            "project_overview": self._generate_project_overview(natural_language_input, project_type),
            "functional_requirements": self._extract_functional_requirements(natural_language_input, context),
            "non_functional_requirements": self._extract_non_functional_requirements(natural_language_input, context),
            "constraints": self._extract_constraints(natural_language_input, context),
            "user_stories": self._generate_user_stories(natural_language_input, context),
            "data_requirements": self._extract_data_requirements(natural_language_input, context)
        }
        
        # 要件をファイルに保存
        self._save_requirements(requirements, project_name)
        
        # RAGエンジンに登録
        self._add_to_knowledge_base(requirements)
        
        self.logger.info(f"プロジェクト '{project_name}' の要件分析が完了しました")
        return requirements
    
    def _generate_project_overview(self, natural_language_input: str, project_type: str) -> str:
        """自然言語入力からプロジェクト概要を生成"""
        # この部分は実際にはLLMを使って生成します
        # 例としてダミー実装を提供
        overview = f"{project_type.capitalize()}プロジェクト: {natural_language_input[:100]}..."
        return overview
    
    def _extract_functional_requirements(self, natural_language_input: str, context: str) -> List[str]:
        """機能要件の抽出"""
        # この部分は実際にはLLMを使って生成します
        # 例としてダミー実装を提供
        return [
            "ユーザー認証機能を提供する",
            "データの作成・読み取り・更新・削除（CRUD）操作をサポートする",
            f"{natural_language_input[:50]}... に関する機能を実装する"
        ]
    
    def _extract_non_functional_requirements(self, natural_language_input: str, context: str) -> Dict[str, str]:
        """非機能要件の抽出"""
        # この部分は実際にはLLMを使って生成します
        # 例としてダミー実装を提供
        return {
            "performance": "ページロード時間は3秒以内であること",
            "security": "ユーザーデータは暗号化して保存すること",
            "usability": "モバイルデバイスでも使いやすいUIを提供すること"
        }
    
    def _extract_constraints(self, natural_language_input: str, context: str) -> List[str]:
        """制約条件の抽出"""
        # この部分は実際にはLLMを使って生成します
        # 例としてダミー実装を提供
        return [
            "モダンなWebブラウザでのみ動作すること",
            "外部APIへの依存を最小限に抑えること"
        ]
    
    def _generate_user_stories(self, natural_language_input: str, context: str) -> List[Dict[str, str]]:
        """ユーザーストーリーの生成"""
        # この部分は実際にはLLMを使って生成します
        # 例としてダミー実装を提供
        return [
            {
                "as_a": "ユーザー",
                "i_want_to": "アカウントを作成する",
                "so_that": "システムにアクセスできるようになる"
            },
            {
                "as_a": "ユーザー",
                "i_want_to": "データを保存する",
                "so_that": "後で参照できる"
            }
        ]
    
    def _extract_data_requirements(self, natural_language_input: str, context: str) -> Dict[str, List[Dict[str, str]]]:
        """データ要件の抽出"""
        # この部分は実際にはLLMを使って生成します
        # 例としてダミー実装を提供
        return {
            "entities": [
                {
                    "name": "User",
                    "attributes": ["id", "name", "email", "password"]
                },
                {
                    "name": "Data",
                    "attributes": ["id", "title", "content", "created_at", "user_id"]
                }
            ]
        }
    
    def _save_requirements(self, requirements: Dict[str, Any], project_name: str):
        """要件をファイルに保存"""
        # 通常の要件ファイル
        filename = f"{project_name.lower().replace(' ', '_')}_requirements.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, ensure_ascii=False, indent=2)
        
        # 履歴用のコピーを作成
        history_filename = f"{project_name.lower().replace(' ', '_')}_v{requirements['version']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        history_filepath = os.path.join(self.history_dir, history_filename)
        
        with open(history_filepath, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"要件を保存しました: {filepath}")
    
    def _add_to_knowledge_base(self, requirements: Dict[str, Any]):
        """要件をRAGエンジンの知識ベースに追加"""
        # 要件を文字列に変換
        content = json.dumps(requirements, ensure_ascii=False, indent=2)
        
        # メタデータを作成
        metadata = {
            "project_name": requirements["project_name"],
            "project_type": requirements["project_type"],
            "version": requirements["version"],
            "type": "requirements",
            "creation_date": requirements["creation_date"]
        }
        
        # RAGエンジンに追加
        self.rag_engine.add_document(content, metadata)
        self.logger.info(f"要件を知識ベースに追加しました: {requirements['project_name']}")
    
    def generate_markdown(self, 
                        requirement_dict: Dict[str, Any], 
                        project_name: str,
                        project_type: str = None) -> str:
        """
        要件辞書からMarkdownドキュメントを生成
        
        Args:
            requirement_dict: 要件辞書
            project_name: プロジェクト名
            project_type: プロジェクトタイプ
            
        Returns:
            Markdownテキスト
        """
        project_type = project_type or requirement_dict.get("project_type", "アプリケーション")
        
        # Markdownヘッダー
        markdown = f"# {project_name} 要件定義書\n\n"
        markdown += f"**バージョン:** {requirement_dict.get('version', '1.0')}\n"
        markdown += f"**作成日:** {datetime.datetime.fromisoformat(requirement_dict.get('creation_date', datetime.datetime.now().isoformat())).strftime('%Y年%m月%d日')}\n\n"
        
        # プロジェクト概要
        markdown += "## プロジェクト概要\n\n"
        markdown += f"{requirement_dict.get('project_overview', 'プロジェクト概要なし')}\n\n"
        
        # 機能要件
        markdown += "## 機能要件\n\n"
        func_req = requirement_dict.get("functional_requirements", [])
        if func_req:
            for i, req in enumerate(func_req, 1):
                markdown += f"{i}. {req}\n"
        else:
            markdown += "機能要件は未定義です。\n"
        markdown += "\n"
        
        # 非機能要件
        markdown += "## 非機能要件\n\n"
        non_func_req = requirement_dict.get("non_functional_requirements", {})
        if non_func_req:
            for key, value in non_func_req.items():
                markdown += f"### {key.capitalize()}\n\n"
                markdown += f"{value}\n\n"
        else:
            markdown += "非機能要件は未定義です。\n\n"
        
        # 制約条件
        markdown += "## 制約条件\n\n"
        constraints = requirement_dict.get("constraints", [])
        if constraints:
            for i, constraint in enumerate(constraints, 1):
                markdown += f"{i}. {constraint}\n"
        else:
            markdown += "制約条件は未定義です。\n"
        markdown += "\n"
        
        # ユーザーストーリー
        markdown += "## ユーザーストーリー\n\n"
        user_stories = requirement_dict.get("user_stories", [])
        if user_stories:
            for i, story in enumerate(user_stories, 1):
                markdown += f"### ストーリー {i}\n\n"
                markdown += f"**As a** {story.get('as_a', 'ユーザー')}, "
                markdown += f"**I want to** {story.get('i_want_to', '機能を使用する')}, "
                markdown += f"**so that** {story.get('so_that', '目的を達成できる')}.\n\n"
        else:
            markdown += "ユーザーストーリーは未定義です。\n\n"
        
        # データ要件
        markdown += "## データ要件\n\n"
        data_req = requirement_dict.get("data_requirements", {})
        entities = data_req.get("entities", [])
        if entities:
            for entity in entities:
                markdown += f"### {entity.get('name', 'Entity')}\n\n"
                markdown += "| 属性 | 説明 |\n"
                markdown += "|------|------|\n"
                for attr in entity.get("attributes", []):
                    markdown += f"| {attr} | |\n"
                markdown += "\n"
        else:
            markdown += "データ要件は未定義です。\n\n"
        
        # ファイルに保存
        output_file = os.path.join(self.output_dir, f"{project_name.lower().replace(' ', '_')}_requirements.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        self.logger.info(f"Markdownドキュメントを生成しました: {output_file}")
        return markdown
    
    def update_requirements(self,
                          project_name: str,
                          additional_input: str) -> Dict[str, Any]:
        """
        既存の要件を更新
        
        Args:
            project_name: プロジェクト名
            additional_input: 追加の要求や変更
            
        Returns:
            更新された要件辞書
        """
        self.logger.info(f"プロジェクト '{project_name}' の要件更新を開始...")
        
        # 既存の要件を読み込み
        filename = f"{project_name.lower().replace(' ', '_')}_requirements.json"
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            self.logger.error(f"要件ファイルが見つかりません: {filepath}")
            return {"error": f"要件ファイルが見つかりません: {filepath}"}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_requirements = json.load(f)
        
        # バージョンを更新
        current_version = existing_requirements.get("version", "1.0")
        new_version = self._increment_version(current_version)
        
        # 更新要件の作成
        updated_requirements = existing_requirements.copy()
        updated_requirements.update({
            "version": new_version,
            "update_date": datetime.datetime.now().isoformat(),
            "update_input": additional_input,
            "previous_version": current_version
        })
        
        # TODO: 実際のLLMを使用して各要件を更新する
        # ここでは仮実装として追加入力を機能要件に追加
        
        # 機能要件の更新
        existing_func_req = existing_requirements.get("functional_requirements", [])
        if isinstance(existing_func_req, list):
            existing_func_req.append(f"追加機能: {additional_input}")
            updated_requirements["functional_requirements"] = existing_func_req
        
        # 要件をファイルに保存
        self._save_requirements(updated_requirements, project_name)
        
        # RAGエンジンに登録
        self._add_to_knowledge_base(updated_requirements)
        
        self.logger.info(f"プロジェクト '{project_name}' の要件更新が完了しました")
        return updated_requirements
    
    def _increment_version(self, version: str) -> str:
        """バージョン番号をインクリメント"""
        parts = version.split('.')
        if len(parts) >= 2:
            major, minor = int(parts[0]), int(parts[1])
            minor += 1
            return f"{major}.{minor}"
        return f"{version}.1"
    
    def compare_versions(self, project_name: str) -> Dict[str, Any]:
        """
        プロジェクトの要件バージョン間の変更を比較
        
        Args:
            project_name: プロジェクト名
            
        Returns:
            比較結果
        """
        self.logger.info(f"プロジェクト '{project_name}' のバージョン比較を開始...")
        
        # 履歴ディレクトリから最新2バージョンを取得
        history_pattern = f"{project_name.lower().replace(' ', '_')}_v*.json"
        history_files = []
        
        for file in os.listdir(self.history_dir):
            if file.startswith(f"{project_name.lower().replace(' ', '_')}_v") and file.endswith(".json"):
                history_files.append(file)
        
        if len(history_files) < 2:
            self.logger.warning(f"比較に必要な2つ以上のバージョンが見つかりません")
            return {"error": "比較に必要な2つ以上のバージョンが見つかりません"}
        
        # タイムスタンプでソート
        history_files.sort(reverse=True)
        
        # 最新と1つ前のバージョンを読み込み
        current_file = os.path.join(self.history_dir, history_files[0])
        previous_file = os.path.join(self.history_dir, history_files[1])
        
        with open(current_file, 'r', encoding='utf-8') as f:
            current = json.load(f)
            
        with open(previous_file, 'r', encoding='utf-8') as f:
            previous = json.load(f)
        
        # 変更点を分析
        comparison = {
            "project_name": project_name,
            "current_version": current.get("version", "不明"),
            "previous_version": previous.get("version", "不明"),
            "comparison_date": datetime.datetime.now().isoformat(),
            "changes": {}
        }
        
        # 変更点の検出
        for key in current.keys():
            if key in ["version", "creation_date", "update_date", "previous_version"]:
                continue
                
            if key not in previous:
                comparison["changes"][key] = {
                    "status": "added",
                    "current": current[key]
                }
            elif current[key] != previous[key]:
                comparison["changes"][key] = {
                    "status": "modified",
                    "current": current[key],
                    "previous": previous[key]
                }
        
        # 削除された項目
        for key in previous.keys():
            if key not in current and key not in ["version", "creation_date", "update_date", "previous_version"]:
                comparison["changes"][key] = {
                    "status": "removed",
                    "previous": previous[key]
                }
        
        # 比較結果をMarkdownで保存
        comparison_md = self._generate_comparison_markdown(comparison)
        output_file = os.path.join(self.output_dir, f"{project_name.lower().replace(' ', '_')}_comparison.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(comparison_md)
        
        self.logger.info(f"バージョン比較が完了しました: {output_file}")
        return comparison
    
    def _generate_comparison_markdown(self, comparison: Dict[str, Any]) -> str:
        """比較結果からMarkdownを生成"""
        markdown = f"# {comparison['project_name']} 要件変更履歴\n\n"
        markdown += f"**現在のバージョン:** {comparison['current_version']}\n"
        markdown += f"**前のバージョン:** {comparison['previous_version']}\n"
        markdown += f"**比較日時:** {datetime.datetime.fromisoformat(comparison['comparison_date']).strftime('%Y年%m月%d日 %H:%M')}\n\n"
        
        markdown += "## 変更点\n\n"
        
        if not comparison.get("changes"):
            markdown += "変更点はありません。\n\n"
        else:
            for key, change in comparison["changes"].items():
                status = change["status"]
                
                if status == "added":
                    markdown += f"### {key} (追加)\n\n"
                    markdown += f"```json\n{json.dumps(change['current'], ensure_ascii=False, indent=2)}\n```\n\n"
                    
                elif status == "removed":
                    markdown += f"### {key} (削除)\n\n"
                    markdown += f"```json\n{json.dumps(change['previous'], ensure_ascii=False, indent=2)}\n```\n\n"
                    
                elif status == "modified":
                    markdown += f"### {key} (変更)\n\n"
                    
                    # リストか辞書の場合は差分を詳細に表示
                    if isinstance(change['current'], (list, dict)) and isinstance(change['previous'], (list, dict)):
                        current_str = json.dumps(change['current'], ensure_ascii=False, indent=2).splitlines()
                        previous_str = json.dumps(change['previous'], ensure_ascii=False, indent=2).splitlines()
                        
                        diff = difflib.unified_diff(
                            previous_str,
                            current_str,
                            lineterm='',
                            n=3
                        )
                        
                        markdown += "```diff\n"
                        for line in diff:
                            markdown += line + "\n"
                        markdown += "```\n\n"
                    else:
                        # それ以外は前後の値を表示
                        markdown += f"**変更前:**\n\n"
                        markdown += f"```\n{change['previous']}\n```\n\n"
                        markdown += f"**変更後:**\n\n"
                        markdown += f"```\n{change['current']}\n```\n\n"
        
        return markdown 