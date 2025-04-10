import os
import argparse
import json
import logging
import datetime
from typing import Dict, Any, List, Optional

from rag_engine import RAGEngine, RAGEngineFeedback
from requirement_generator import RequirementGenerator
from design_generator import DesignGenerator
from code_generator import CodeGenerator
from test_generator import TestGenerator

class SnowballDevApp:
    """
    雪だるま式開発ツールのメインアプリケーション
    """
    
    def __init__(self, output_dir: str = "./snowball_output"):
        """
        アプリケーションの初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # ロギングの設定
        self.setup_logging()
        
        # 各モジュールの初期化
        self.logger.info("RAGエンジンを初期化中...")
        self.rag_engine = RAGEngine(
            embedding_model_name="intfloat/multilingual-e5-large",
            knowledge_base_path=os.path.join(output_dir, "knowledge_base")
        )
        
        self.rag_feedback = RAGEngineFeedback(self.rag_engine)
        
        self.logger.info("要件定義生成器を初期化中...")
        self.requirement_generator = RequirementGenerator(
            rag_engine=self.rag_engine,
            output_dir=os.path.join(output_dir, "requirements")
        )
        
        self.logger.info("設計生成器を初期化中...")
        self.design_generator = DesignGenerator(
            rag_engine=self.rag_engine,
            output_dir=os.path.join(output_dir, "designs")
        )
        
        self.logger.info("コード生成器を初期化中...")
        self.code_generator = CodeGenerator(
            rag_engine=self.rag_engine,
            output_dir=os.path.join(output_dir, "generated_code")
        )
        
        self.logger.info("テスト生成器を初期化中...")
        self.test_generator = TestGenerator(
            rag_engine=self.rag_engine,
            output_dir=os.path.join(output_dir, "generated_tests")
        )
        
        self.logger.info("初期化完了")
    
    def setup_logging(self):
        """ロギングの設定"""
        log_dir = os.path.join(self.output_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"snowball_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # ロガーの設定
        self.logger = logging.getLogger("SnowballDevApp")
        self.logger.setLevel(logging.INFO)
        
        # ファイルハンドラの追加
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # コンソールハンドラの追加
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def crawl_resources(self, urls: List[str] = None, repo_urls: List[str] = None):
        """
        WebリソースとリポジトリをクローリングしてRAGに追加
        
        Args:
            urls: クローリングするWebページのURL
            repo_urls: クローリングするGitリポジトリのURL
        """
        self.logger.info("リソースクローリングを開始...")
        
        if urls:
            self.logger.info(f"{len(urls)}件のWebリソースをクローリング中...")
            self.rag_engine.crawl_web_resources(urls)
        
        if repo_urls:
            self.logger.info(f"{len(repo_urls)}件のリポジトリをマイニング中...")
            for repo_url in repo_urls:
                self.rag_engine.mine_code_repository(repo_url)
        
        self.logger.info("リソースクローリングが完了しました")
    
    def generate_project(self, 
                        project_name: str, 
                        natural_language_input: str,
                        project_type: str = "web_app",
                        language: str = "python") -> Dict[str, Any]:
        """
        自然言語入力からプロジェクトを生成（要件定義から実装まで）
        
        Args:
            project_name: プロジェクト名
            natural_language_input: 自然言語による要求
            project_type: プロジェクトタイプ
            language: 主要プログラミング言語
            
        Returns:
            生成プロセスの結果と各ステップの出力へのパス
        """
        self.logger.info(f"プロジェクト '{project_name}' の生成を開始...")
        
        results = {
            "project_name": project_name,
            "project_type": project_type,
            "language": language,
            "timestamp": datetime.datetime.now().isoformat(),
            "steps": {}
        }
        
        # ステップ1: 要件定義の生成
        self.logger.info("要件定義を生成中...")
        try:
            requirements = self.requirement_generator.analyze_requirements(
                natural_language_input=natural_language_input,
                project_name=project_name,
                project_type=project_type
            )
            
            requirements_md = self.requirement_generator.generate_markdown(
                requirement_dict=requirements,
                project_name=project_name,
                project_type=project_type
            )
            
            results["steps"]["requirements"] = {
                "status": "success",
                "output": requirements,
                "markdown_path": os.path.join(self.requirement_generator.output_dir, f"{project_name.lower().replace(' ', '_')}_requirements.md")
            }
            
            self.logger.info("要件定義の生成が完了しました")
        except Exception as e:
            self.logger.error(f"要件定義の生成中にエラーが発生しました: {str(e)}")
            results["steps"]["requirements"] = {
                "status": "error",
                "error": str(e)
            }
            return results
        
        # ステップ2: アーキテクチャ設計の生成
        self.logger.info("アーキテクチャ設計を生成中...")
        try:
            architecture = self.design_generator.generate_architecture(
                requirement_dict=requirements,
                project_name=project_name,
                project_type=project_type
            )
            
            design_doc = self.design_generator.generate_design_document(
                architecture=architecture,
                project_name=project_name,
                requirement_dict=requirements
            )
            
            results["steps"]["architecture"] = {
                "status": "success",
                "output": architecture,
                "design_doc_path": os.path.join(self.design_generator.output_dir, f"{project_name.lower().replace(' ', '_')}_design.md")
            }
            
            self.logger.info("アーキテクチャ設計の生成が完了しました")
        except Exception as e:
            self.logger.error(f"アーキテクチャ設計の生成中にエラーが発生しました: {str(e)}")
            results["steps"]["architecture"] = {
                "status": "error",
                "error": str(e)
            }
            return results
        
        # ステップ3: シーケンス図の生成
        self.logger.info("主要ユースケースのシーケンス図を生成中...")
        try:
            # 要件から主要ユースケースを抽出
            use_cases = self._extract_use_cases(requirements)
            
            sequence_diagrams = self.design_generator.generate_sequence_diagrams(
                architecture=architecture,
                use_cases=use_cases
            )
            
            results["steps"]["sequence_diagrams"] = {
                "status": "success",
                "output": sequence_diagrams,
                "diagrams_path": self.design_generator.output_dir
            }
            
            self.logger.info(f"{len(sequence_diagrams)}件のシーケンス図の生成が完了しました")
        except Exception as e:
            self.logger.error(f"シーケンス図の生成中にエラーが発生しました: {str(e)}")
            results["steps"]["sequence_diagrams"] = {
                "status": "error",
                "error": str(e)
            }
            # シーケンス図のエラーは致命的ではないので続行
        
        # ステップ4: プロジェクト構造の生成
        self.logger.info("プロジェクト構造を生成中...")
        try:
            project_structure = self.code_generator.generate_project_structure(
                architecture=architecture,
                project_name=project_name,
                primary_language=language
            )
            
            self.code_generator.create_directory_structure(
                structure=project_structure["structure"],
                base_dir=project_structure["project_dir"]
            )
            
            results["steps"]["project_structure"] = {
                "status": "success",
                "output": project_structure,
                "project_dir": project_structure["project_dir"]
            }
            
            self.logger.info("プロジェクト構造の生成が完了しました")
        except Exception as e:
            self.logger.error(f"プロジェクト構造の生成中にエラーが発生しました: {str(e)}")
            results["steps"]["project_structure"] = {
                "status": "error",
                "error": str(e)
            }
            return results
        
        # ステップ5: 設定ファイルの生成
        self.logger.info("プロジェクト設定ファイルを生成中...")
        try:
            config_files = self.code_generator.generate_configuration_files(
                architecture=architecture,
                project_structure=project_structure,
                primary_language=language
            )
            
            results["steps"]["config_files"] = {
                "status": "success",
                "output": config_files
            }
            
            self.logger.info(f"{len(config_files)}件の設定ファイルの生成が完了しました")
        except Exception as e:
            self.logger.error(f"設定ファイルの生成中にエラーが発生しました: {str(e)}")
            results["steps"]["config_files"] = {
                "status": "error",
                "error": str(e)
            }
            # 設定ファイルのエラーは致命的ではないので続行
        
        # ステップ6: コンポーネントの生成
        self.logger.info("コンポーネントコードを生成中...")
        try:
            components = self.code_generator.generate_all_components(
                architecture=architecture,
                project_structure=project_structure,
                primary_language=language
            )
            
            results["steps"]["components"] = {
                "status": "success",
                "output": components,
                "component_count": len(components)
            }
            
            self.logger.info(f"{len(components)}件のコンポーネントの生成が完了しました")
        except Exception as e:
            self.logger.error(f"コンポーネントの生成中にエラーが発生しました: {str(e)}")
            results["steps"]["components"] = {
                "status": "error",
                "error": str(e)
            }
            # 一部コンポーネントのエラーは致命的ではないので続行
        
        # ステップ7: 統合テストの生成
        self.logger.info("統合テストを生成中...")
        try:
            integration_tests = self.test_generator.generate_integration_tests(
                project_dir=project_structure["project_dir"],
                language=language,
                architecture=architecture
            )
            
            results["steps"]["integration_tests"] = {
                "status": "success",
                "output": integration_tests
            }
            
            self.logger.info("統合テストの生成が完了しました")
        except Exception as e:
            self.logger.error(f"統合テストの生成中にエラーが発生しました: {str(e)}")
            results["steps"]["integration_tests"] = {
                "status": "error",
                "error": str(e)
            }
            # テストのエラーは致命的ではないので続行
        
        # ステップ8: コード検証
        self.logger.info("生成されたコードを検証中...")
        try:
            validation_results = self.code_generator.validate_generated_code(
                project_dir=project_structure["project_dir"],
                language=language
            )
            
            results["steps"]["validation"] = {
                "status": validation_results["status"],
                "output": validation_results
            }
            
            if validation_results["status"] == "success":
                self.logger.info("コード検証が成功しました")
            else:
                self.logger.warning(f"コード検証で{len(validation_results['errors'])}件のエラーが見つかりました")
        except Exception as e:
            self.logger.error(f"コード検証中にエラーが発生しました: {str(e)}")
            results["steps"]["validation"] = {
                "status": "error",
                "error": str(e)
            }
            # 検証のエラーは致命的ではないので続行
        
        # 結果の保存
        results_path = os.path.join(self.output_dir, f"{project_name.lower().replace(' ', '_')}_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"プロジェクト '{project_name}' の生成が完了しました")
        self.logger.info(f"結果は {results_path} に保存されました")
        
        return results
    
    def _extract_use_cases(self, requirements: Dict[str, Any]) -> List[str]:
        """要件から主要ユースケースを抽出"""
        use_cases = []
        
        # 機能要件からユースケースを抽出
        if "functional_requirements" in requirements:
            func_req = requirements["functional_requirements"]
            
            if isinstance(func_req, str):
                # 文字列から行単位でユースケースを抽出
                lines = func_req.split('\n')
                for line in lines:
                    line = line.strip()
                    # 箇条書きや番号付きリストのパターンを検出
                    if re.match(r'^[\d\-\*\.]+\s+', line):
                        # 先頭の記号を削除
                        use_case = re.sub(r'^[\d\-\*\.]+\s+', '', line)
                        if use_case and len(use_case) > 10:  # 短すぎるものは除外
                            use_cases.append(use_case)
            elif isinstance(func_req, list):
                # リストからユースケースを直接抽出
                for item in func_req:
                    if isinstance(item, str) and len(item) > 10:
                        use_cases.append(item)
                    elif isinstance(item, dict) and "description" in item:
                        use_cases.append(item["description"])
        
        # ユースケースが少ない場合は一般的なものを追加
        if len(use_cases) < 2:
            if "project_overview" in requirements:
                use_cases.append(f"メイン機能の実行: {requirements['project_overview'][:50]}")
            use_cases.append("ユーザー認証と認可")
            use_cases.append("データの作成と保存")
            use_cases.append("データの取得と表示")
            
        # 最大5件に制限
        return use_cases[:5]
    
    def update_project(self, 
                      project_name: str, 
                      additional_input: str) -> Dict[str, Any]:
        """
        既存プロジェクトを追加入力で更新
        
        Args:
            project_name: プロジェクト名
            additional_input: 追加の要求や変更
            
        Returns:
            更新プロセスの結果
        """
        self.logger.info(f"プロジェクト '{project_name}' の更新を開始...")
        
        results = {
            "project_name": project_name,
            "update_input": additional_input,
            "timestamp": datetime.datetime.now().isoformat(),
            "steps": {}
        }
        
        # ステップ1: 要件定義の更新
        self.logger.info("要件定義を更新中...")
        try:
            updated_requirements = self.requirement_generator.update_requirements(
                project_name=project_name,
                additional_input=additional_input
            )
            
            if "error" in updated_requirements:
                self.logger.error(f"要件定義の更新に失敗しました: {updated_requirements['error']}")
                results["steps"]["requirements_update"] = {
                    "status": "error",
                    "error": updated_requirements["error"]
                }
                return results
            
            requirements_md = self.requirement_generator.generate_markdown(
                requirement_dict=updated_requirements,
                project_name=project_name
            )
            
            results["steps"]["requirements_update"] = {
                "status": "success",
                "output": updated_requirements,
                "markdown_path": os.path.join(self.requirement_generator.output_dir, f"{project_name.lower().replace(' ', '_')}_requirements.md")
            }
            
            # 変更比較レポートの生成
            comparison = self.requirement_generator.compare_versions(project_name)
            results["steps"]["requirements_comparison"] = {
                "status": "success",
                "output": comparison,
                "comparison_path": os.path.join(self.requirement_generator.output_dir, f"{project_name.lower().replace(' ', '_')}_comparison.md")
            }
            
            self.logger.info("要件定義の更新が完了しました")
        except Exception as e:
            self.logger.error(f"要件定義の更新中にエラーが発生しました: {str(e)}")
            results["steps"]["requirements_update"] = {
                "status": "error",
                "error": str(e)
            }
            return results
        
        # ステップ2: アーキテクチャの更新
        self.logger.info("アーキテクチャを更新中...")
        try:
            architecture = self.design_generator.generate_architecture(
                requirement_dict=updated_requirements,
                project_name=project_name,
                project_type=updated_requirements.get("project_type", "web_app")
            )
            
            design_doc = self.design_generator.generate_design_document(
                architecture=architecture,
                project_name=project_name,
                requirement_dict=updated_requirements
            )
            
            results["steps"]["architecture_update"] = {
                "status": "success",
                "output": architecture,
                "design_doc_path": os.path.join(self.design_generator.output_dir, f"{project_name.lower().replace(' ', '_')}_design.md")
            }
            
            self.logger.info("アーキテクチャの更新が完了しました")
        except Exception as e:
            self.logger.error(f"アーキテクチャの更新中にエラーが発生しました: {str(e)}")
            results["steps"]["architecture_update"] = {
                "status": "error",
                "error": str(e)
            }
            return results
        
        # 既存のプロジェクトディレクトリを検索
        project_dir = None
        for entry in self.code_generator.generation_history:
            if entry["project_name"] == project_name:
                project_dir = entry["project_dir"]
                break
        
        if not project_dir or not os.path.exists(project_dir):
            self.logger.error(f"プロジェクト '{project_name}' のディレクトリが見つかりません")
            results["steps"]["code_update"] = {
                "status": "error",
                "error": f"プロジェクトディレクトリが見つかりません"
            }
            return results
        
        # ステップ3: コードの更新
        self.logger.info("コードを更新中...")
        try:
            # 変更されたコンポーネントを特定
            new_components = []
            modified_components = []
            
            if "components" in architecture:
                # 新しいアーキテクチャのコンポーネント
                new_arch_components = []
                if isinstance(architecture["components"], list):
                    new_arch_components = [comp["name"] if isinstance(comp, dict) and "name" in comp else str(comp) 
                                          for comp in architecture["components"]]
                elif isinstance(architecture["components"], dict):
                    new_arch_components = list(architecture["components"].keys())
                
                # 既存コンポーネントの検出
                existing_components = []
                for root, _, files in os.walk(project_dir):
                    for file in files:
                        if file.endswith((".py", ".js", ".ts", ".java")):
                            component_name = os.path.splitext(file)[0]
                            if component_name.startswith("Test"):
                                continue  # テストファイルは除外
                            existing_components.append(component_name)
                
                # 新規コンポーネントと更新コンポーネントを特定
                for component in new_arch_components:
                    if component in existing_components:
                        modified_components.append(component)
                    else:
                        new_components.append(component)
            
            # 言語の検出
            language = None
            for entry in self.code_generator.generation_history:
                if entry["project_name"] == project_name:
                    language = entry["primary_language"]
                    break
            
            if not language:
                language = "python"  # デフォルト
            
            # 新規コンポーネントの生成
            generated_new = []
            for component in new_components:
                new_component = self.code_generator.generate_component(
                    architecture=architecture,
                    component_name=component,
                    language=language,
                    project_dir=project_dir
                )
                generated_new.append(new_component)
            
            # 既存コンポーネントの更新
            updated_components = []
            for component in modified_components[:3]:  # 最初の3つだけ更新（時間を節約）
                # 既存ファイルの検出
                component_file = None
                for root, _, files in os.walk(project_dir):
                    for file in files:
                        if file.startswith(component) and file.endswith((".py", ".js", ".ts", ".java")):
                            component_file = os.path.join(root, file)
                            break
                    if component_file:
                        break
                
                if component_file:
                    # コンポーネントの再生成
                    updated_component = self.code_generator.generate_component(
                        architecture=architecture,
                        component_name=component,
                        language=language,
                        project_dir=project_dir
                    )
                    updated_components.append(updated_component)
            
            results["steps"]["code_update"] = {
                "status": "success",
                "new_components": generated_new,
                "updated_components": updated_components
            }
            
            self.logger.info(f"{len(generated_new)}個の新規コンポーネントと{len(updated_components)}個の更新コンポーネントの生成が完了しました")
        except Exception as e:
            self.logger.error(f"コードの更新中にエラーが発生しました: {str(e)}")
            results["steps"]["code_update"] = {
                "status": "error",
                "error": str(e)
            }
            # コード更新のエラーは致命的ではないので続行
        
        # ステップ4: テストの更新
        self.logger.info("テストを更新中...")
        try:
            # 統合テストの再生成
            integration_tests = self.test_generator.generate_integration_tests(
                project_dir=project_dir,
                language=language,
                architecture=architecture
            )
            
            results["steps"]["test_update"] = {
                "status": "success",
                "output": integration_tests
            }
            
            self.logger.info("テストの更新が完了しました")
        except Exception as e:
            self.logger.error(f"テストの更新中にエラーが発生しました: {str(e)}")
            results["steps"]["test_update"] = {
                "status": "error",
                "error": str(e)
            }
            # テスト更新のエラーは致命的ではないので続行
        
        # 結果の保存
        results_path = os.path.join(self.output_dir, f"{project_name.lower().replace(' ', '_')}_update_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"プロジェクト '{project_name}' の更新が完了しました")
        self.logger.info(f"結果は {results_path} に保存されました")
        
        return results
    
    def run_cli(self):
        """コマンドラインインターフェースを実行"""
        parser = argparse.ArgumentParser(description="雪だるま式開発ツール")
        subparsers = parser.add_subparsers(dest="command", help="実行するコマンド")
        
        # crawlコマンド
        crawl_parser = subparsers.add_parser("crawl", help="Webリソースとリポジトリをクローリング")
        crawl_parser.add_argument("--urls", nargs="+", help="クローリングするWebページのURL")
        crawl_parser.add_argument("--repos", nargs="+", help="クローリングするGitリポジトリのURL")
        
        # generateコマンド
        generate_parser = subparsers.add_parser("generate", help="プロジェクトを生成")
        generate_parser.add_argument("--name", required=True, help="プロジェクト名")
        generate_parser.add_argument("--input", required=True, help="自然言語による要求")
        generate_parser.add_argument("--type", default="web_app", help="プロジェクトタイプ")
        generate_parser.add_argument("--language", default="python", help="主要プログラミング言語")
        
        # updateコマンド
        update_parser = subparsers.add_parser("update", help="既存プロジェクトを更新")
        update_parser.add_argument("--name", required=True, help="プロジェクト名")
        update_parser.add_argument("--input", required=True, help="追加の要求や変更")
        
        args = parser.parse_args()
        
        if args.command == "crawl":
            if not args.urls and not args.repos:
                parser.error("--urls または --repos のいずれかを指定してください")
            self.crawl_resources(urls=args.urls, repo_urls=args.repos)
        
        elif args.command == "generate":
            self.generate_project(
                project_name=args.name,
                natural_language_input=args.input,
                project_type=args.type,
                language=args.language
            )
        
        elif args.command == "update":
            self.update_project(
                project_name=args.name,
                additional_input=args.input
            )
        
        else:
            parser.print_help()


if __name__ == "__main__":
    app = SnowballDevApp()
    app.run_cli()