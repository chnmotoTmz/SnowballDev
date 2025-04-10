import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional

from rag_engine import RAGEngine

class CodeGenerator:
    """
    コード生成器
    プロジェクト構造とファイル構成の自動生成、コンポーネントの実装を行う
    """
    
    def __init__(self, rag_engine: RAGEngine, output_dir: str = "./generated_code"):
        """
        コード生成器の初期化
        
        Args:
            rag_engine: RAGエンジンのインスタンス
            output_dir: 出力ディレクトリのパス
        """
        self.rag_engine = rag_engine
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger = logging.getLogger("CodeGenerator")
        self.generation_history = []  # 生成履歴を記録
    
    def generate_project_structure(self,
                                 architecture: Dict[str, Any],
                                 project_name: str,
                                 primary_language: str) -> Dict[str, Any]:
        """
        プロジェクト構造の生成
        
        Args:
            architecture: アーキテクチャ辞書
            project_name: プロジェクト名
            primary_language: 主要言語（python, javascript, java, etc.）
            
        Returns:
            プロジェクト構造の情報
        """
        self.logger.info(f"プロジェクト '{project_name}' の構造を生成中...")
        
        # プロジェクトディレクトリの作成
        project_dir = os.path.join(self.output_dir, project_name.lower().replace(' ', '_'))
        os.makedirs(project_dir, exist_ok=True)
        
        # プロジェクトタイプに基づいて適切な構造を選択
        architecture_type = architecture.get("architecture_type", "generic")
        project_structure = self._select_project_structure(
            architecture_type=architecture_type,
            primary_language=primary_language
        )
        
        # 生成情報を記録
        structure_info = {
            "project_name": project_name,
            "primary_language": primary_language,
            "architecture_type": architecture_type,
            "project_dir": project_dir,
            "structure": project_structure,
            "creation_date": datetime.datetime.now().isoformat()
        }
        
        # 生成履歴に追加
        self.generation_history.append(structure_info)
        
        self.logger.info(f"プロジェクト構造の設計が完了しました: {project_dir}")
        return structure_info
    
    def _select_project_structure(self, 
                               architecture_type: str, 
                               primary_language: str) -> Dict[str, Any]:
        """プロジェクトタイプと言語に基づいて適切な構造を選択"""
        if architecture_type == "web_app":
            if primary_language == "python":
                return self._create_python_web_app_structure()
            elif primary_language in ["javascript", "typescript"]:
                return self._create_js_web_app_structure()
            elif primary_language == "java":
                return self._create_java_web_app_structure()
        elif architecture_type == "api_service":
            if primary_language == "python":
                return self._create_python_api_structure()
            elif primary_language in ["javascript", "typescript"]:
                return self._create_js_api_structure()
        # その他のタイプ...
        
        # デフォルトの汎用構造
        return self._create_generic_structure(primary_language)
    
    def _create_python_web_app_structure(self) -> Dict[str, Any]:
        """Pythonのウェブアプリケーション構造を生成"""
        return {
            "directories": [
                {"path": "", "files": ["README.md", "requirements.txt", ".gitignore", "setup.py"]},
                {"path": "app", "files": ["__init__.py", "main.py", "config.py"]},
                {"path": "app/controllers", "files": ["__init__.py", "base_controller.py"]},
                {"path": "app/models", "files": ["__init__.py", "base_model.py"]},
                {"path": "app/views", "files": ["__init__.py"]},
                {"path": "app/static", "files": [".gitkeep"]},
                {"path": "app/templates", "files": ["base.html", "index.html"]},
                {"path": "tests", "files": ["__init__.py", "conftest.py"]},
                {"path": "docs", "files": ["README.md"]}
            ]
        }
    
    def _create_js_web_app_structure(self) -> Dict[str, Any]:
        """JavaScript/TypeScriptのウェブアプリケーション構造を生成"""
        return {
            "directories": [
                {"path": "", "files": ["README.md", "package.json", ".gitignore", "tsconfig.json"]},
                {"path": "src", "files": ["index.js", "app.js", "config.js"]},
                {"path": "src/controllers", "files": ["index.js", "baseController.js"]},
                {"path": "src/models", "files": ["index.js", "baseModel.js"]},
                {"path": "src/views", "files": ["index.js"]},
                {"path": "public", "files": ["index.html", "style.css"]},
                {"path": "tests", "files": ["setup.js"]},
                {"path": "docs", "files": ["README.md"]}
            ]
        }
    
    def _create_java_web_app_structure(self) -> Dict[str, Any]:
        """Javaのウェブアプリケーション構造を生成"""
        return {
            "directories": [
                {"path": "", "files": ["README.md", "pom.xml", ".gitignore", "build.gradle"]},
                {"path": "src/main/java/com/app", "files": ["Application.java", "Config.java"]},
                {"path": "src/main/java/com/app/controllers", "files": ["BaseController.java"]},
                {"path": "src/main/java/com/app/models", "files": ["BaseModel.java"]},
                {"path": "src/main/java/com/app/views", "files": []},
                {"path": "src/main/resources", "files": ["application.properties"]},
                {"path": "src/main/resources/static", "files": [".gitkeep"]},
                {"path": "src/main/resources/templates", "files": ["index.html"]},
                {"path": "src/test/java/com/app", "files": ["ApplicationTests.java"]},
                {"path": "docs", "files": ["README.md"]}
            ]
        }
    
    def _create_python_api_structure(self) -> Dict[str, Any]:
        """PythonのAPIサービス構造を生成"""
        return {
            "directories": [
                {"path": "", "files": ["README.md", "requirements.txt", ".gitignore", "setup.py"]},
                {"path": "api", "files": ["__init__.py", "main.py", "config.py"]},
                {"path": "api/routes", "files": ["__init__.py", "base_route.py"]},
                {"path": "api/models", "files": ["__init__.py", "base_model.py"]},
                {"path": "api/services", "files": ["__init__.py", "base_service.py"]},
                {"path": "tests", "files": ["__init__.py", "conftest.py"]},
                {"path": "docs", "files": ["README.md", "api.md"]}
            ]
        }
    
    def _create_js_api_structure(self) -> Dict[str, Any]:
        """JavaScript/TypeScriptのAPIサービス構造を生成"""
        return {
            "directories": [
                {"path": "", "files": ["README.md", "package.json", ".gitignore", "tsconfig.json"]},
                {"path": "src", "files": ["index.js", "app.js", "config.js"]},
                {"path": "src/routes", "files": ["index.js", "baseRoute.js"]},
                {"path": "src/models", "files": ["index.js", "baseModel.js"]},
                {"path": "src/services", "files": ["index.js", "baseService.js"]},
                {"path": "tests", "files": ["setup.js"]},
                {"path": "docs", "files": ["README.md", "api.md"]}
            ]
        }
    
    def _create_generic_structure(self, primary_language: str) -> Dict[str, Any]:
        """汎用的なプロジェクト構造を生成"""
        if primary_language == "python":
            return {
                "directories": [
                    {"path": "", "files": ["README.md", "requirements.txt", ".gitignore", "setup.py"]},
                    {"path": "src", "files": ["__init__.py", "main.py"]},
                    {"path": "tests", "files": ["__init__.py", "test_main.py"]},
                    {"path": "docs", "files": ["README.md"]}
                ]
            }
        elif primary_language in ["javascript", "typescript"]:
            return {
                "directories": [
                    {"path": "", "files": ["README.md", "package.json", ".gitignore"]},
                    {"path": "src", "files": ["index.js", "main.js"]},
                    {"path": "tests", "files": ["main.test.js"]},
                    {"path": "docs", "files": ["README.md"]}
                ]
            }
        elif primary_language == "java":
            return {
                "directories": [
                    {"path": "", "files": ["README.md", "pom.xml", ".gitignore"]},
                    {"path": "src/main/java/com/app", "files": ["Main.java"]},
                    {"path": "src/test/java/com/app", "files": ["MainTest.java"]},
                    {"path": "docs", "files": ["README.md"]}
                ]
            }
        else:
            # その他の言語用のデフォルト構造
            return {
                "directories": [
                    {"path": "", "files": ["README.md", ".gitignore"]},
                    {"path": "src", "files": []},
                    {"path": "tests", "files": []},
                    {"path": "docs", "files": ["README.md"]}
                ]
            }
    
    def create_directory_structure(self,
                                 structure: Dict[str, List[Dict[str, Any]]],
                                 base_dir: str):
        """
        ディレクトリ構造の作成
        
        Args:
            structure: ディレクトリ構造の定義
            base_dir: ベースディレクトリのパス
        """
        self.logger.info(f"ディレクトリ構造を作成中: {base_dir}")
        
        # 各ディレクトリとファイルを作成
        for directory_info in structure.get("directories", []):
            dir_path = os.path.join(base_dir, directory_info["path"])
            os.makedirs(dir_path, exist_ok=True)
            
            # ディレクトリ内のファイルを作成
            for file_name in directory_info.get("files", []):
                file_path = os.path.join(dir_path, file_name)
                
                # 既にファイルが存在する場合はスキップ
                if os.path.exists(file_path):
                    self.logger.info(f"ファイルが既に存在します: {file_path}")
                    continue
                
                # 空のファイルを作成
                with open(file_path, 'w', encoding='utf-8') as f:
                    pass
                
                self.logger.info(f"ファイルを作成しました: {file_path}")
        
        self.logger.info(f"ディレクトリ構造の作成が完了しました: {base_dir}")
    
    def generate_configuration_files(self,
                                  architecture: Dict[str, Any],
                                  project_structure: Dict[str, Any],
                                  primary_language: str) -> List[str]:
        """
        設定ファイルの生成
        
        Args:
            architecture: アーキテクチャ辞書
            project_structure: プロジェクト構造情報
            primary_language: 主要言語
            
        Returns:
            生成されたファイルのパスのリスト
        """
        self.logger.info("設定ファイルを生成中...")
        
        project_dir = project_structure["project_dir"]
        architecture_type = architecture.get("architecture_type", "generic")
        generated_files = []
        
        # 言語とプロジェクトタイプに基づいて設定ファイルを生成
        if primary_language == "python":
            generated_files.extend(self._generate_python_config_files(project_dir, architecture_type))
        elif primary_language in ["javascript", "typescript"]:
            generated_files.extend(self._generate_js_config_files(project_dir, architecture_type))
        elif primary_language == "java":
            generated_files.extend(self._generate_java_config_files(project_dir, architecture_type))
        
        # 共通の設定ファイル
        generated_files.extend(self._generate_common_config_files(project_dir, architecture_type))
        
        self.logger.info(f"{len(generated_files)}件の設定ファイルを生成しました")
        return generated_files
    
    def _generate_python_config_files(self, project_dir: str, architecture_type: str) -> List[str]:
        """Python用の設定ファイルを生成"""
        generated_files = []
        
        # requirements.txt
        req_path = os.path.join(project_dir, "requirements.txt")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write("# Generated by SnowballDev\n\n")
            
            # 共通のライブラリ
            f.write("# Common libraries\n")
            f.write("python-dotenv==0.19.1\n")
            f.write("pytest==6.2.5\n\n")
            
            # プロジェクトタイプに応じたライブラリ
            if architecture_type == "web_app":
                f.write("# Web application libraries\n")
                f.write("flask==2.0.1\n")
                f.write("jinja2==3.0.1\n")
                f.write("werkzeug==2.0.1\n")
                f.write("flask-sqlalchemy==2.5.1\n")
            elif architecture_type == "api_service":
                f.write("# API service libraries\n")
                f.write("fastapi==0.68.1\n")
                f.write("uvicorn==0.15.0\n")
                f.write("pydantic==1.8.2\n")
                f.write("sqlalchemy==1.4.25\n")
        
        generated_files.append(req_path)
        
        # setup.py
        setup_path = os.path.join(project_dir, "setup.py")
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write("# Generated by SnowballDev\n\n")
            f.write("from setuptools import setup, find_packages\n\n")
            f.write("setup(\n")
            f.write(f"    name='{os.path.basename(project_dir)}',\n")
            f.write("    version='0.1.0',\n")
            f.write("    description='Generated by SnowballDev',\n")
            f.write("    author='',\n")
            f.write("    author_email='',\n")
            f.write("    packages=find_packages(),\n")
            f.write("    install_requires=[\n")
            f.write("        # Requirements\n")
            f.write("    ],\n")
            f.write(")\n")
        
        generated_files.append(setup_path)
        
        return generated_files
    
    def _generate_js_config_files(self, project_dir: str, architecture_type: str) -> List[str]:
        """JavaScript/TypeScript用の設定ファイルを生成"""
        generated_files = []
        
        # package.json
        pkg_path = os.path.join(project_dir, "package.json")
        with open(pkg_path, 'w', encoding='utf-8') as f:
            pkg_data = {
                "name": os.path.basename(project_dir),
                "version": "0.1.0",
                "description": "Generated by SnowballDev",
                "main": "src/index.js",
                "scripts": {
                    "start": "node src/index.js",
                    "test": "jest"
                },
                "keywords": [],
                "author": "",
                "license": "MIT",
                "dependencies": {},
                "devDependencies": {
                    "jest": "^27.2.4"
                }
            }
            
            # プロジェクトタイプに応じた依存関係
            if architecture_type == "web_app":
                pkg_data["dependencies"].update({
                    "express": "^4.17.1",
                    "ejs": "^3.1.6",
                    "mongoose": "^6.0.8"
                })
                pkg_data["scripts"]["dev"] = "nodemon src/index.js"
                pkg_data["devDependencies"]["nodemon"] = "^2.0.13"
            elif architecture_type == "api_service":
                pkg_data["dependencies"].update({
                    "express": "^4.17.1",
                    "body-parser": "^1.19.0",
                    "cors": "^2.8.5",
                    "mongoose": "^6.0.8"
                })
                pkg_data["scripts"]["dev"] = "nodemon src/index.js"
                pkg_data["devDependencies"]["nodemon"] = "^2.0.13"
            
            json.dump(pkg_data, f, ensure_ascii=False, indent=2)
        
        generated_files.append(pkg_path)
        
        # TypeScriptの場合はtsconfig.jsonも生成
        if os.path.exists(os.path.join(project_dir, "tsconfig.json")):
            ts_path = os.path.join(project_dir, "tsconfig.json")
            with open(ts_path, 'w', encoding='utf-8') as f:
                ts_data = {
                    "compilerOptions": {
                        "target": "ES2018",
                        "module": "commonjs",
                        "outDir": "./dist",
                        "rootDir": "./src",
                        "strict": True,
                        "esModuleInterop": True,
                        "skipLibCheck": True,
                        "forceConsistentCasingInFileNames": True
                    },
                    "include": ["src/**/*"],
                    "exclude": ["node_modules", "**/*.test.ts"]
                }
                json.dump(ts_data, f, ensure_ascii=False, indent=2)
            
            generated_files.append(ts_path)
        
        return generated_files
    
    def _generate_java_config_files(self, project_dir: str, architecture_type: str) -> List[str]:
        """Java用の設定ファイルを生成"""
        generated_files = []
        
        # pom.xml
        pom_path = os.path.join(project_dir, "pom.xml")
        with open(pom_path, 'w', encoding='utf-8') as f:
            f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            f.write("<project xmlns=\"http://maven.apache.org/POM/4.0.0\"\n")
            f.write("         xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
            f.write("         xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd\">\n")
            f.write("    <modelVersion>4.0.0</modelVersion>\n")
            
            if architecture_type in ["web_app", "api_service"]:
                f.write("    <parent>\n")
                f.write("        <groupId>org.springframework.boot</groupId>\n")
                f.write("        <artifactId>spring-boot-starter-parent</artifactId>\n")
                f.write("        <version>2.5.5</version>\n")
                f.write("    </parent>\n")
            
            f.write(f"    <groupId>com.app</groupId>\n")
            f.write(f"    <artifactId>{os.path.basename(project_dir)}</artifactId>\n")
            f.write("    <version>0.1.0</version>\n")
            f.write(f"    <name>{os.path.basename(project_dir)}</name>\n")
            f.write("    <description>Generated by SnowballDev</description>\n")
            
            f.write("    <properties>\n")
            f.write("        <java.version>11</java.version>\n")
            f.write("    </properties>\n")
            
            f.write("    <dependencies>\n")
            if architecture_type == "web_app":
                f.write("        <dependency>\n")
                f.write("            <groupId>org.springframework.boot</groupId>\n")
                f.write("            <artifactId>spring-boot-starter-web</artifactId>\n")
                f.write("        </dependency>\n")
                f.write("        <dependency>\n")
                f.write("            <groupId>org.springframework.boot</groupId>\n")
                f.write("            <artifactId>spring-boot-starter-thymeleaf</artifactId>\n")
                f.write("        </dependency>\n")
            elif architecture_type == "api_service":
                f.write("        <dependency>\n")
                f.write("            <groupId>org.springframework.boot</groupId>\n")
                f.write("            <artifactId>spring-boot-starter-web</artifactId>\n")
                f.write("        </dependency>\n")
                f.write("        <dependency>\n")
                f.write("            <groupId>org.springframework.boot</groupId>\n")
                f.write("            <artifactId>spring-boot-starter-data-jpa</artifactId>\n")
                f.write("        </dependency>\n")
            
            f.write("        <dependency>\n")
            f.write("            <groupId>org.springframework.boot</groupId>\n")
            f.write("            <artifactId>spring-boot-starter-test</artifactId>\n")
            f.write("            <scope>test</scope>\n")
            f.write("        </dependency>\n")
            f.write("    </dependencies>\n")
            
            f.write("    <build>\n")
            f.write("        <plugins>\n")
            if architecture_type in ["web_app", "api_service"]:
                f.write("            <plugin>\n")
                f.write("                <groupId>org.springframework.boot</groupId>\n")
                f.write("                <artifactId>spring-boot-maven-plugin</artifactId>\n")
                f.write("            </plugin>\n")
            
            f.write("        </plugins>\n")
            f.write("    </build>\n")
            
            f.write("</project>\n")
        
        generated_files.append(pom_path)
        
        return generated_files
    
    def _generate_common_config_files(self, project_dir: str, architecture_type: str) -> List[str]:
        """共通の設定ファイルを生成"""
        generated_files = []
        
        # .gitignore
        gitignore_path = os.path.join(project_dir, ".gitignore")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("# Generated by SnowballDev\n\n")
            
            # 共通のignore
            f.write("# Common\n")
            f.write(".env\n")
            f.write(".vscode/\n")
            f.write(".idea/\n")
            f.write("*.log\n\n")
            
            # Python
            f.write("# Python\n")
            f.write("__pycache__/\n")
            f.write("*.py[cod]\n")
            f.write("*$py.class\n")
            f.write("*.so\n")
            f.write(".Python\n")
            f.write("env/\n")
            f.write("build/\n")
            f.write("develop-eggs/\n")
            f.write("dist/\n")
            f.write("downloads/\n")
            f.write("eggs/\n")
            f.write(".eggs/\n")
            f.write("lib/\n")
            f.write("lib64/\n")
            f.write("parts/\n")
            f.write("sdist/\n")
            f.write("var/\n")
            f.write("*.egg-info/\n")
            f.write(".installed.cfg\n")
            f.write("*.egg\n\n")
            
            # JavaScript/Node
            f.write("# JavaScript/Node\n")
            f.write("node_modules/\n")
            f.write("npm-debug.log\n")
            f.write("yarn-debug.log\n")
            f.write("yarn-error.log\n")
            f.write(".pnp/\n")
            f.write(".pnp.js\n")
            f.write("coverage/\n")
            f.write("dist/\n")
            f.write("build/\n\n")
            
            # Java
            f.write("# Java\n")
            f.write("target/\n")
            f.write("*.class\n")
            f.write("*.jar\n")
            f.write("*.war\n")
            f.write("*.ear\n")
            f.write(".classpath\n")
            f.write(".project\n")
            f.write(".settings/\n")
        
        generated_files.append(gitignore_path)
        
        # README.md
        readme_path = os.path.join(project_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {os.path.basename(project_dir)}\n\n")
            f.write("Generated by SnowballDev\n\n")
            
            f.write("## Overview\n\n")
            f.write("A brief description of the project goes here.\n\n")
            
            f.write("## Getting Started\n\n")
            f.write("### Prerequisites\n\n")
            f.write("- List of prerequisites\n\n")
            
            f.write("### Installation\n\n")
            f.write("```bash\n")
            if os.path.exists(os.path.join(project_dir, "requirements.txt")):
                f.write("# Install dependencies\n")
                f.write("pip install -r requirements.txt\n")
            elif os.path.exists(os.path.join(project_dir, "package.json")):
                f.write("# Install dependencies\n")
                f.write("npm install\n")
            elif os.path.exists(os.path.join(project_dir, "pom.xml")):
                f.write("# Build the project\n")
                f.write("./mvnw clean install\n")
            f.write("```\n\n")
            
            f.write("## Usage\n\n")
            f.write("```bash\n")
            if os.path.exists(os.path.join(project_dir, "requirements.txt")):
                f.write("# Run the application\n")
                if architecture_type == "web_app":
                    f.write("python app/main.py\n")
                elif architecture_type == "api_service":
                    f.write("python api/main.py\n")
                else:
                    f.write("python src/main.py\n")
            elif os.path.exists(os.path.join(project_dir, "package.json")):
                f.write("# Run the application\n")
                f.write("npm start\n")
            elif os.path.exists(os.path.join(project_dir, "pom.xml")):
                f.write("# Run the application\n")
                f.write("./mvnw spring-boot:run\n")
            f.write("```\n\n")
            
            f.write("## Project Structure\n\n")
            f.write("```\n")
            f.write("A description of the project structure will go here.\n")
            f.write("```\n")
        
        generated_files.append(readme_path)
        
        return generated_files 