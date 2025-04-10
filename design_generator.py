import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional

from rag_engine import RAGEngine

class DesignGenerator:
    """
    設計生成器
    要件からシステムアーキテクチャを設計する
    """
    
    def __init__(self, rag_engine: RAGEngine, output_dir: str = "./designs"):
        """
        設計生成器の初期化
        
        Args:
            rag_engine: RAGエンジンのインスタンス
            output_dir: 出力ディレクトリのパス
        """
        self.rag_engine = rag_engine
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 図表出力用のディレクトリ
        self.diagrams_dir = os.path.join(output_dir, "diagrams")
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
        self.logger = logging.getLogger("DesignGenerator")
    
    def generate_architecture(self,
                            requirement_dict: Dict[str, Any],
                            project_name: str,
                            project_type: str = "web_app") -> Dict[str, Any]:
        """
        要件からシステムアーキテクチャを生成
        
        Args:
            requirement_dict: 要件辞書
            project_name: プロジェクト名
            project_type: プロジェクトタイプ
            
        Returns:
            アーキテクチャ辞書
        """
        self.logger.info(f"プロジェクト '{project_name}' のアーキテクチャ設計を開始...")
        
        # RAGエンジンを使用して類似アーキテクチャを検索
        self.logger.info("類似アーキテクチャを検索中...")
        similar_designs = self.rag_engine.search(
            query=f"プロジェクトタイプ: {project_type}, 機能: {' '.join(requirement_dict.get('functional_requirements', [])[:3])}",
            top_k=3,
            filter_criteria={"type": "architecture"}
        )
        
        # 類似設計の情報をコンテキストとして利用
        context = ""
        if similar_designs:
            self.logger.info(f"{len(similar_designs)}件の類似アーキテクチャが見つかりました")
            for i, design in enumerate(similar_designs):
                context += f"\n--- 類似アーキテクチャ {i+1} ---\n"
                context += design["content"]
        else:
            self.logger.info("類似アーキテクチャは見つかりませんでした")
        
        # プロジェクトタイプに基づいて適切なアーキテクチャパターンを選択
        architecture = self._select_architecture_pattern(project_type, requirement_dict)
        
        # アーキテクチャをカスタマイズ
        self._customize_architecture(architecture, requirement_dict, project_name)
        
        # アーキテクチャをファイルに保存
        self._save_architecture(architecture, project_name)
        
        # RAGエンジンに登録
        self._add_to_knowledge_base(architecture, project_name, project_type)
        
        self.logger.info(f"プロジェクト '{project_name}' のアーキテクチャ設計が完了しました")
        return architecture
    
    def _select_architecture_pattern(self, 
                                   project_type: str, 
                                   requirement_dict: Dict[str, Any]) -> Dict[str, Any]:
        """プロジェクトタイプに基づいて適切なアーキテクチャパターンを選択"""
        if project_type == "web_app":
            return self._create_web_app_architecture(requirement_dict)
        elif project_type == "api_service":
            return self._create_api_service_architecture(requirement_dict)
        elif project_type == "mobile_app":
            return self._create_mobile_app_architecture(requirement_dict)
        elif project_type == "desktop_app":
            return self._create_desktop_app_architecture(requirement_dict)
        else:
            return self._create_generic_architecture(requirement_dict)
    
    def _create_web_app_architecture(self, requirement_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Webアプリケーションのアーキテクチャを生成"""
        # 実際にはLLMを使ってより詳細なアーキテクチャを生成します
        # これはダミー実装です
        return {
            "architecture_type": "web_app",
            "pattern": "MVC",
            "frontend": {
                "framework": "React",
                "components": ["Header", "Footer", "Main", "Auth", "Dashboard"]
            },
            "backend": {
                "framework": "Express.js",
                "api": {
                    "version": "v1",
                    "endpoints": [
                        {"path": "/auth", "methods": ["POST"]},
                        {"path": "/users", "methods": ["GET", "POST", "PUT", "DELETE"]},
                        {"path": "/data", "methods": ["GET", "POST", "PUT", "DELETE"]}
                    ]
                }
            },
            "database": {
                "type": "MongoDB",
                "models": [
                    {"name": "User", "fields": ["id", "name", "email", "password"]},
                    {"name": "Data", "fields": ["id", "title", "content", "userId", "createdAt"]}
                ]
            },
            "deployment": {
                "environment": "Docker",
                "services": ["frontend", "backend", "database"]
            }
        }
    
    def _create_api_service_architecture(self, requirement_dict: Dict[str, Any]) -> Dict[str, Any]:
        """APIサービスのアーキテクチャを生成"""
        # 実際にはLLMを使ってより詳細なアーキテクチャを生成します
        # これはダミー実装です
        return {
            "architecture_type": "api_service",
            "pattern": "RESTful",
            "api": {
                "framework": "FastAPI",
                "version": "v1",
                "endpoints": [
                    {"path": "/auth", "methods": ["POST"]},
                    {"path": "/resources", "methods": ["GET", "POST", "PUT", "DELETE"]}
                ]
            },
            "database": {
                "type": "PostgreSQL",
                "models": [
                    {"name": "User", "fields": ["id", "name", "email", "password"]},
                    {"name": "Resource", "fields": ["id", "name", "data", "userId", "createdAt"]}
                ]
            },
            "deployment": {
                "environment": "Kubernetes",
                "services": ["api", "database", "cache"]
            }
        }
    
    def _create_mobile_app_architecture(self, requirement_dict: Dict[str, Any]) -> Dict[str, Any]:
        """モバイルアプリのアーキテクチャを生成"""
        # ダミー実装
        return {
            "architecture_type": "mobile_app",
            "pattern": "MVVM",
            "app": {
                "framework": "Flutter",
                "screens": ["Login", "Home", "Profile", "Settings"]
            },
            "backend": {
                "type": "Firebase",
                "services": ["Authentication", "Firestore", "Storage"]
            }
        }
    
    def _create_desktop_app_architecture(self, requirement_dict: Dict[str, Any]) -> Dict[str, Any]:
        """デスクトップアプリのアーキテクチャを生成"""
        # ダミー実装
        return {
            "architecture_type": "desktop_app",
            "pattern": "MVVM",
            "ui": {
                "framework": "Electron",
                "components": ["MainWindow", "Dialog", "Menu"]
            },
            "data": {
                "storage": "SQLite",
                "models": ["User", "Document", "Settings"]
            }
        }
    
    def _create_generic_architecture(self, requirement_dict: Dict[str, Any]) -> Dict[str, Any]:
        """汎用的なアーキテクチャを生成"""
        # ダミー実装
        return {
            "architecture_type": "generic",
            "pattern": "Layered",
            "layers": [
                {"name": "Presentation", "components": ["UI", "API"]},
                {"name": "Business", "components": ["Services", "Logic"]},
                {"name": "Data", "components": ["Repository", "Models"]}
            ]
        }
    
    def _customize_architecture(self, 
                             architecture: Dict[str, Any], 
                             requirement_dict: Dict[str, Any],
                             project_name: str):
        """要件に基づいてアーキテクチャをカスタマイズ"""
        # プロジェクト情報を追加
        architecture["project_name"] = project_name
        architecture["creation_date"] = datetime.datetime.now().isoformat()
        
        # 要件から機能コンポーネントを抽出
        functional_requirements = requirement_dict.get("functional_requirements", [])
        if functional_requirements:
            # コンポーネント名のリストを生成
            components = [f"Component{i}" for i, _ in enumerate(functional_requirements, 1)]
            architecture["components"] = components
        
        # データ要件からデータモデルを抽出
        data_requirements = requirement_dict.get("data_requirements", {})
        entities = data_requirements.get("entities", [])
        if entities:
            # アーキテクチャタイプに基づいて適切な場所にデータモデルを挿入
            if architecture["architecture_type"] == "web_app":
                # データベースモデルを更新
                architecture["database"]["models"] = [
                    {"name": entity["name"], "fields": entity["attributes"]}
                    for entity in entities
                ]
            elif architecture["architecture_type"] == "api_service":
                architecture["database"]["models"] = [
                    {"name": entity["name"], "fields": entity["attributes"]}
                    for entity in entities
                ]
    
    def _save_architecture(self, architecture: Dict[str, Any], project_name: str):
        """アーキテクチャをファイルに保存"""
        filename = f"{project_name.lower().replace(' ', '_')}_architecture.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(architecture, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"アーキテクチャを保存しました: {filepath}")
    
    def _add_to_knowledge_base(self, 
                           architecture: Dict[str, Any], 
                           project_name: str,
                           project_type: str):
        """アーキテクチャをRAGエンジンの知識ベースに追加"""
        # アーキテクチャを文字列に変換
        content = json.dumps(architecture, ensure_ascii=False, indent=2)
        
        # メタデータを作成
        metadata = {
            "project_name": project_name,
            "project_type": project_type,
            "architecture_type": architecture["architecture_type"],
            "type": "architecture",
            "creation_date": architecture.get("creation_date", datetime.datetime.now().isoformat())
        }
        
        # RAGエンジンに追加
        self.rag_engine.add_document(content, metadata)
        self.logger.info(f"アーキテクチャを知識ベースに追加しました: {project_name}")
    
    def generate_design_document(self, 
                               architecture: Dict[str, Any], 
                               project_name: str,
                               requirement_dict: Dict[str, Any]) -> str:
        """
        アーキテクチャからデザインドキュメントを生成
        
        Args:
            architecture: アーキテクチャ辞書
            project_name: プロジェクト名
            requirement_dict: 要件辞書
            
        Returns:
            Markdownテキスト
        """
        self.logger.info(f"プロジェクト '{project_name}' のデザインドキュメントを生成...")
        
        # Markdownヘッダー
        markdown = f"# {project_name} 設計書\n\n"
        markdown += f"**作成日:** {datetime.datetime.now().strftime('%Y年%m月%d日')}\n\n"
        
        # アーキテクチャ概要
        markdown += "## アーキテクチャ概要\n\n"
        markdown += f"**アーキテクチャタイプ:** {architecture.get('architecture_type', '不明')}\n"
        markdown += f"**アーキテクチャパターン:** {architecture.get('pattern', '不明')}\n\n"
        
        # コンポーネント構成
        markdown += "## システム構成\n\n"
        
        # プロジェクトタイプに応じた構成図の説明
        if architecture.get("architecture_type") == "web_app":
            markdown += self._generate_web_app_section(architecture)
        elif architecture.get("architecture_type") == "api_service":
            markdown += self._generate_api_section(architecture)
        elif architecture.get("architecture_type") == "mobile_app":
            markdown += self._generate_mobile_app_section(architecture)
        else:
            # 汎用的な構成
            if "layers" in architecture:
                markdown += "### レイヤー構成\n\n"
                for layer in architecture["layers"]:
                    markdown += f"- **{layer['name']}**\n"
                    for component in layer.get("components", []):
                        markdown += f"  - {component}\n"
                markdown += "\n"
            
            if "components" in architecture:
                markdown += "### コンポーネント\n\n"
                for component in architecture["components"]:
                    markdown += f"- {component}\n"
                markdown += "\n"
        
        # データモデル
        markdown += "## データモデル\n\n"
        
        # データモデルの抽出
        models = []
        if "database" in architecture and "models" in architecture["database"]:
            models = architecture["database"]["models"]
        
        if models:
            for model in models:
                markdown += f"### {model['name']}\n\n"
                markdown += "| フィールド | 型 | 説明 |\n"
                markdown += "|----------|------|------|\n"
                for field in model.get("fields", []):
                    markdown += f"| {field} | | |\n"
                markdown += "\n"
        else:
            markdown += "データモデルは未定義です。\n\n"
        
        # シーケンス図への参照
        markdown += "## シーケンス図\n\n"
        markdown += "主要なユースケースのシーケンス図は以下のディレクトリに保存されています：\n\n"
        markdown += f"`{self.diagrams_dir}`\n\n"
        
        # ファイルに保存
        output_file = os.path.join(self.output_dir, f"{project_name.lower().replace(' ', '_')}_design.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        self.logger.info(f"デザインドキュメントを生成しました: {output_file}")
        return markdown
    
    def _generate_web_app_section(self, architecture: Dict[str, Any]) -> str:
        """Webアプリケーションの構成セクションを生成"""
        section = "### フロントエンド\n\n"
        if "frontend" in architecture:
            frontend = architecture["frontend"]
            section += f"**フレームワーク:** {frontend.get('framework', '不明')}\n\n"
            section += "**コンポーネント:**\n\n"
            for component in frontend.get("components", []):
                section += f"- {component}\n"
            section += "\n"
        
        section += "### バックエンド\n\n"
        if "backend" in architecture:
            backend = architecture["backend"]
            section += f"**フレームワーク:** {backend.get('framework', '不明')}\n\n"
            
            if "api" in backend:
                section += "**API:**\n\n"
                section += f"- バージョン: {backend['api'].get('version', 'v1')}\n"
                section += "- エンドポイント:\n"
                for endpoint in backend['api'].get('endpoints', []):
                    methods = ", ".join(endpoint.get("methods", []))
                    section += f"  - {endpoint.get('path', '/')} [{methods}]\n"
                section += "\n"
        
        section += "### データベース\n\n"
        if "database" in architecture:
            database = architecture["database"]
            section += f"**タイプ:** {database.get('type', '不明')}\n\n"
        
        section += "### デプロイメント\n\n"
        if "deployment" in architecture:
            deployment = architecture["deployment"]
            section += f"**環境:** {deployment.get('environment', '不明')}\n\n"
            section += "**サービス:**\n\n"
            for service in deployment.get("services", []):
                section += f"- {service}\n"
            section += "\n"
        
        return section
    
    def _generate_api_section(self, architecture: Dict[str, Any]) -> str:
        """APIサービスの構成セクションを生成"""
        section = "### API\n\n"
        if "api" in architecture:
            api = architecture["api"]
            section += f"**フレームワーク:** {api.get('framework', '不明')}\n"
            section += f"**バージョン:** {api.get('version', 'v1')}\n\n"
            
            section += "**エンドポイント:**\n\n"
            for endpoint in api.get('endpoints', []):
                methods = ", ".join(endpoint.get("methods", []))
                section += f"- {endpoint.get('path', '/')} [{methods}]\n"
            section += "\n"
        
        section += "### データベース\n\n"
        if "database" in architecture:
            database = architecture["database"]
            section += f"**タイプ:** {database.get('type', '不明')}\n\n"
        
        section += "### デプロイメント\n\n"
        if "deployment" in architecture:
            deployment = architecture["deployment"]
            section += f"**環境:** {deployment.get('environment', '不明')}\n\n"
            section += "**サービス:**\n\n"
            for service in deployment.get("services", []):
                section += f"- {service}\n"
            section += "\n"
        
        return section
    
    def _generate_mobile_app_section(self, architecture: Dict[str, Any]) -> str:
        """モバイルアプリの構成セクションを生成"""
        section = "### アプリケーション\n\n"
        if "app" in architecture:
            app = architecture["app"]
            section += f"**フレームワーク:** {app.get('framework', '不明')}\n\n"
            section += "**画面:**\n\n"
            for screen in app.get("screens", []):
                section += f"- {screen}\n"
            section += "\n"
        
        section += "### バックエンド連携\n\n"
        if "backend" in architecture:
            backend = architecture["backend"]
            section += f"**タイプ:** {backend.get('type', '不明')}\n\n"
            section += "**サービス:**\n\n"
            for service in backend.get("services", []):
                section += f"- {service}\n"
            section += "\n"
        
        return section
    
    def generate_sequence_diagrams(self, 
                                 architecture: Dict[str, Any], 
                                 use_cases: List[str]) -> Dict[str, str]:
        """
        主要ユースケースのシーケンス図を生成
        
        Args:
            architecture: アーキテクチャ辞書
            use_cases: ユースケースのリスト
            
        Returns:
            ユースケース名とダイアグラムパスのマッピング
        """
        self.logger.info(f"{len(use_cases)}件のシーケンス図を生成中...")
        
        diagrams = {}
        
        for i, use_case in enumerate(use_cases):
            # ユースケース名を正規化
            use_case_name = use_case.replace(" ", "_").lower()[:30]
            
            # PlantUMLのコード生成（実際にはLLMを使用）
            puml_code = self._generate_sequence_diagram_code(use_case, architecture)
            
            # ファイルに保存
            filename = f"sequence_{i+1}_{use_case_name}.puml"
            filepath = os.path.join(self.diagrams_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(puml_code)
            
            diagrams[use_case] = filepath
            self.logger.info(f"シーケンス図を生成しました: {filepath}")
        
        return diagrams
    
    def _generate_sequence_diagram_code(self, use_case: str, architecture: Dict[str, Any]) -> str:
        """
        ユースケースとアーキテクチャからPlantUMLコードを生成
        
        Args:
            use_case: ユースケース
            architecture: アーキテクチャ辞書
            
        Returns:
            PlantUMLコード
        """
        # これは簡略化した実装。実際にはLLMを使ってユースケースに合わせた詳細なシーケンス図を生成します
        
        # シーケンス図の参加者を特定
        participants = []
        
        if architecture.get("architecture_type") == "web_app":
            participants.append("ユーザー")
            participants.append("ブラウザ")
            if "frontend" in architecture:
                participants.extend([f"Frontend:{comp}" for comp in architecture["frontend"].get("components", [])[:2]])
            if "backend" in architecture:
                participants.extend([f"Backend:{endpoint['path']}" for endpoint in architecture["backend"].get("api", {}).get("endpoints", [])[:2]])
            if "database" in architecture:
                participants.extend([f"DB:{model['name']}" for model in architecture["database"].get("models", [])[:2]])
        
        elif architecture.get("architecture_type") == "api_service":
            participants.append("クライアント")
            if "api" in architecture:
                participants.extend([f"API:{endpoint['path']}" for endpoint in architecture["api"].get("endpoints", [])[:3]])
            if "database" in architecture:
                participants.extend([f"DB:{model['name']}" for model in architecture["database"].get("models", [])[:2]])
        
        elif architecture.get("architecture_type") == "mobile_app":
            participants.append("ユーザー")
            if "app" in architecture:
                participants.extend([f"Screen:{screen}" for screen in architecture["app"].get("screens", [])[:3]])
            if "backend" in architecture:
                participants.extend([f"Backend:{service}" for service in architecture["backend"].get("services", [])[:2]])
        
        else:
            participants = ["Actor", "System", "Database"]
        
        # シーケンス図テンプレート
        puml = f"""@startuml {use_case}
title {use_case}

"""
        
        # 参加者の定義
        for participant in participants:
            puml += f"participant \"{participant}\"\n"
        
        puml += "\n"
        
        # 一般的なフローの例
        puml += "== 開始 ==\n\n"
        
        # アーキテクチャタイプに基づいたシーケンスの生成
        if "ユーザー" in participants:
            puml += "ユーザー -> ブラウザ: アクションを実行\n"
            if "Frontend:Main" in participants:
                puml += "ブラウザ -> Frontend:Main: イベント発火\n"
                if "Backend:/data" in participants:
                    puml += "Frontend:Main -> Backend:/data: APIリクエスト\n"
                    if "DB:User" in participants:
                        puml += "Backend:/data -> DB:User: データ検索\n"
                        puml += "DB:User --> Backend:/data: 結果返却\n"
                    puml += "Backend:/data --> Frontend:Main: レスポンス\n"
                puml += "Frontend:Main --> ブラウザ: 画面更新\n"
            puml += "ブラウザ --> ユーザー: 結果表示\n"
        elif "クライアント" in participants:
            if "API:/resources" in participants:
                puml += "クライアント -> API:/resources: リクエスト送信\n"
                if "DB:Resource" in participants:
                    puml += "API:/resources -> DB:Resource: データ操作\n"
                    puml += "DB:Resource --> API:/resources: 結果返却\n"
                puml += "API:/resources --> クライアント: レスポンス\n"
        
        puml += "\n== 終了 ==\n"
        puml += "@enduml"
        
        return puml 