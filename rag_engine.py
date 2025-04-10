import os
import json
import logging
import datetime
import hashlib
import re
import requests
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlparse

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import git
from bs4 import BeautifulSoup
import html2text

class RAGEngine:
    """
    Retrieval-Augmented Generation エンジン
    Webリソースやコードリポジトリのクローリング、知識ベースの構築、類似情報の検索を行う
    """
    
    def __init__(self, 
                embedding_model_name: str = "intfloat/multilingual-e5-large",
                knowledge_base_path: str = "./knowledge_base"):
        """
        RAGエンジンの初期化
        
        Args:
            embedding_model_name: 埋め込みモデルの名前
            knowledge_base_path: 知識ベースの保存先ディレクトリ
        """
        self.embedding_model_name = embedding_model_name
        self.knowledge_base_path = knowledge_base_path
        os.makedirs(knowledge_base_path, exist_ok=True)
        
        # 埋め込みモデルの初期化
        self.logger = logging.getLogger("RAGEngine")
        self.logger.info(f"埋め込みモデル {embedding_model_name} を読み込み中...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # インデックスの初期化
        self.index_path = os.path.join(knowledge_base_path, "faiss_index.bin")
        self.documents_path = os.path.join(knowledge_base_path, "documents.json")
        
        # 既存のインデックスを読み込むか、新規作成
        if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
            self.load_index()
        else:
            self.create_new_index()
    
    def create_new_index(self):
        """新しいFAISSインデックスを作成"""
        self.logger.info("新しいインデックスを作成中...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.save_index()
    
    def load_index(self):
        """既存のFAISSインデックスとドキュメントを読み込み"""
        self.logger.info("既存のインデックスを読み込み中...")
        self.index = faiss.read_index(self.index_path)
        
        with open(self.documents_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        
        self.logger.info(f"{len(self.documents)}件のドキュメントを読み込みました")
    
    def save_index(self):
        """インデックスとドキュメントを保存"""
        self.logger.info("インデックスを保存中...")
        faiss.write_index(self.index, self.index_path)
        
        with open(self.documents_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def add_document(self, 
                    content: str, 
                    metadata: Dict[str, Any],
                    chunk_size: int = 1000,
                    chunk_overlap: int = 200):
        """
        テキストコンテンツをチャンキングしてインデックスに追加
        
        Args:
            content: テキストコンテンツ
            metadata: ドキュメントのメタデータ
            chunk_size: チャンクのサイズ（文字数）
            chunk_overlap: チャンクのオーバーラップ（文字数）
        """
        # コンテンツのチャンキング
        chunks = self._text_chunking(content, chunk_size, chunk_overlap)
        
        # 各チャンクを処理
        for i, chunk in enumerate(chunks):
            # チャンクIDを生成
            chunk_id = hashlib.md5(f"{metadata.get('source', '')}_{i}".encode()).hexdigest()
            
            # チャンクのメタデータを作成
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # チャンクを埋め込みベクトルに変換
            embedding = self.embedding_model.encode([chunk])[0]
            
            # インデックスに追加
            self.index.add(np.array([embedding], dtype=np.float32))
            
            # ドキュメントリストに追加
            self.documents.append({
                "content": chunk,
                "metadata": chunk_metadata,
                "vector_id": len(self.documents)
            })
        
        # 変更を保存
        self.save_index()
        
        return len(chunks)
    
    def _text_chunking(self, 
                      text: str, 
                      chunk_size: int = 1000, 
                      chunk_overlap: int = 200) -> List[str]:
        """
        テキストを重複ありのチャンクに分割
        
        Args:
            text: 分割するテキスト
            chunk_size: チャンクのサイズ（文字数）
            chunk_overlap: チャンクのオーバーラップ（文字数）
            
        Returns:
            チャンクのリスト
        """
        # 段落や文で分割するためのパターン
        split_pattern = r"(?<=\n\n|\.\s|\?\s|\!\s)"
        segments = re.split(split_pattern, text)
        segments = [s.strip() for s in segments if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for segment in segments:
            # セグメントが非常に長い場合は強制的に分割
            if len(segment) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # 長いセグメントを単純に分割
                for i in range(0, len(segment), chunk_size - chunk_overlap):
                    sub_segment = segment[i:i + chunk_size]
                    if len(sub_segment) > 0.5 * chunk_size:  # 小さすぎるチャンクは避ける
                        chunks.append(sub_segment)
            else:
                # 現在のチャンクにセグメントを追加するとサイズオーバーする場合
                if len(current_chunk) + len(segment) > chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = segment
                else:
                    # 空のチャンクならそのまま追加、そうでなければスペースを入れて追加
                    if not current_chunk:
                        current_chunk = segment
                    else:
                        current_chunk += " " + segment
        
        # 最後のチャンクを追加
        if current_chunk and len(current_chunk) > 0.3 * chunk_size:  # 小さすぎるチャンクは避ける
            chunks.append(current_chunk)
        
        return chunks
    
    def search(self, 
              query: str, 
              top_k: int = 5, 
              filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        クエリに類似したドキュメントを検索
        
        Args:
            query: 検索クエリ
            top_k: 返す結果の数
            filter_criteria: メタデータによるフィルタリング条件
            
        Returns:
            類似ドキュメントのリスト（コンテンツ、メタデータ、類似度スコア）
        """
        # クエリを埋め込みベクトルに変換
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        # Faissでの検索（より多めに結果を取得してからフィルタリング）
        search_k = min(top_k * 3, len(self.documents))
        if search_k == 0:
            return []
            
        distances, indices = self.index.search(query_embedding, search_k)
        
        # 結果の整形とフィルタリング
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0 or idx >= len(self.documents):
                continue
                
            document = self.documents[idx]
            
            # フィルタリング条件があれば適用
            if filter_criteria and not self._match_filter(document["metadata"], filter_criteria):
                continue
            
            # スコアを計算（距離から類似度に変換: 1 / (1 + dist)）
            similarity_score = 1 / (1 + dist)
            
            results.append({
                "content": document["content"],
                "metadata": document["metadata"],
                "score": similarity_score
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _match_filter(self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]) -> bool:
        """フィルタリング条件にメタデータが一致するか確認"""
        for key, value in filter_criteria.items():
            if key not in metadata:
                return False
                
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
                
        return True
    
    def crawl_web_resources(self, urls: List[str], max_depth: int = 1):
        """
        Webリソースをクローリングして知識ベースに追加
        
        Args:
            urls: クローリングするURLのリスト
            max_depth: クローリングの最大深度（リンクを辿る段階）
        """
        self.logger.info(f"{len(urls)}件のWebリソースのクローリングを開始...")
        
        for url in urls:
            self._crawl_url(url, max_depth=max_depth, current_depth=0, visited=set())
            
        self.logger.info("Webリソースのクローリングが完了しました")
    
    def _crawl_url(self, 
                  url: str, 
                  max_depth: int, 
                  current_depth: int, 
                  visited: set):
        """再帰的にURLをクローリング"""
        # 既に訪問済みのURLはスキップ
        if url in visited:
            return
            
        visited.add(url)
        
        # URLのドメインを取得
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        try:
            self.logger.info(f"URLをクローリング中: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # HTMLをテキストに変換
            soup = BeautifulSoup(response.content, "html.parser")
            
            # 不要な要素を削除（スクリプト、スタイル、ナビゲーションなど）
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
                
            # HTML to Text変換
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = True
            text_content = converter.handle(str(soup))
            
            # リンクをプレーンテキストに変換
            text_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text_content)
            
            # ドキュメントとして追加
            metadata = {
                "source": url,
                "type": "web_page",
                "domain": domain,
                "title": soup.title.text if soup.title else url,
                "crawl_date": datetime.datetime.now().isoformat()
            }
            
            chunks_added = self.add_document(text_content, metadata)
            self.logger.info(f"URLを追加しました: {url} ({chunks_added}チャンク)")
            
            # 最大深度に達していなければリンクを辿る
            if current_depth < max_depth:
                # ページ内の同一ドメインのリンクを収集
                links = []
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    
                    # 相対パスを絶対パスに変換
                    if href.startswith("/"):
                        href = f"{domain}{href}"
                    
                    # 同一ドメインのリンクのみを追加
                    if href.startswith(domain) and href not in visited:
                        links.append(href)
                
                # リンクを再帰的にクローリング（最大20件まで）
                for link in links[:20]:
                    self._crawl_url(link, max_depth, current_depth + 1, visited)
                
        except Exception as e:
            self.logger.error(f"URLのクローリング中にエラーが発生しました: {url} - {str(e)}")
    
    def mine_code_repository(self, repo_url: str, temp_dir: str = "./temp_repos"):
        """
        Gitリポジトリをクローンして知識ベースに追加
        
        Args:
            repo_url: GitリポジトリのURL
            temp_dir: 一時ディレクトリのパス
        """
        self.logger.info(f"リポジトリのマイニングを開始: {repo_url}")
        
        # リポジトリ名を取得
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_dir = os.path.join(temp_dir, repo_name)
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            
            # リポジトリをクローンまたは更新
            if os.path.exists(repo_dir):
                # 既存のリポジトリを更新
                self.logger.info(f"既存のリポジトリを更新中: {repo_name}")
                repo = git.Repo(repo_dir)
                repo.remotes.origin.pull()
            else:
                # 新しいリポジトリをクローン
                self.logger.info(f"リポジトリをクローン中: {repo_name}")
                repo = git.Repo.clone_from(repo_url, repo_dir)
            
            # ファイルの処理
            total_files = 0
            processed_files = 0
            
            for root, _, files in os.walk(repo_dir):
                # .gitディレクトリはスキップ
                if ".git" in root.split(os.sep):
                    continue
                    
                for file in files:
                    total_files += 1
                    
                    # コードファイルのみを処理
                    if self._is_code_file(file):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, repo_dir)
                        
                        try:
                            # ファイルを読み込み
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # メタデータを作成
                            metadata = {
                                "source": repo_url,
                                "repo_name": repo_name,
                                "file_path": rel_path,
                                "file_name": file,
                                "file_extension": os.path.splitext(file)[1],
                                "type": "code",
                                "mining_date": datetime.datetime.now().isoformat()
                            }
                            
                            # ドキュメントとして追加
                            chunks_added = self.add_document(content, metadata)
                            processed_files += 1
                        except Exception as e:
                            self.logger.error(f"ファイルの処理中にエラーが発生しました: {rel_path} - {str(e)}")
            
            self.logger.info(f"リポジトリのマイニングが完了しました: {repo_name} ({processed_files}/{total_files}ファイルを処理)")
            
        except Exception as e:
            self.logger.error(f"リポジトリのマイニング中にエラーが発生しました: {repo_url} - {str(e)}")
    
    def _is_code_file(self, filename: str) -> bool:
        """ファイル名からコードファイルかどうかを判定"""
        code_extensions = [
            # Python
            '.py', '.pyw', '.ipynb',
            # Web言語
            '.html', '.css', '.js', '.ts', '.jsx', '.tsx', 
            # Java
            '.java', '.kt', '.groovy',
            # C系言語
            '.c', '.cpp', '.h', '.hpp', '.cs',
            # その他
            '.go', '.rb', '.php', '.scala', '.swift', '.rs',
            # 設定ファイル
            '.json', '.yaml', '.yml', '.xml', '.toml'
        ]
        
        ext = os.path.splitext(filename)[1].lower()
        return ext in code_extensions


class RAGEngineFeedback:
    """
    RAGエンジンのフィードバック処理
    検索結果の評価と改善を行う
    """
    
    def __init__(self, rag_engine: RAGEngine):
        """
        フィードバックシステムの初期化
        
        Args:
            rag_engine: RAGエンジンのインスタンス
        """
        self.rag_engine = rag_engine
        self.logger = logging.getLogger("RAGEngineFeedback")
        
        # フィードバックの保存先
        self.feedback_path = os.path.join(self.rag_engine.knowledge_base_path, "feedback.json")
        self.load_feedback()
    
    def load_feedback(self):
        """フィードバックデータの読み込み"""
        if os.path.exists(self.feedback_path):
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                self.feedback_data = json.load(f)
        else:
            self.feedback_data = {
                "query_feedback": [],  # クエリとその結果に対するフィードバック
                "document_feedback": {}  # ドキュメントIDに対するフィードバック
            }
    
    def save_feedback(self):
        """フィードバックデータの保存"""
        with open(self.feedback_path, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
    
    def add_query_feedback(self, 
                          query: str, 
                          results: List[Dict[str, Any]], 
                          rating: int, 
                          comment: str = None):
        """
        検索クエリとその結果に対するフィードバックを追加
        
        Args:
            query: 検索クエリ
            results: 検索結果
            rating: 評価（1-5）
            comment: コメント
        """
        # 結果からメタデータだけを抽出
        result_metadata = []
        for result in results:
            if "metadata" in result and "chunk_id" in result["metadata"]:
                result_metadata.append({
                    "chunk_id": result["metadata"]["chunk_id"],
                    "score": result.get("score", 0)
                })
        
        # フィードバックを追加
        feedback = {
            "query": query,
            "timestamp": datetime.datetime.now().isoformat(),
            "rating": rating,
            "comment": comment,
            "results": result_metadata
        }
        
        self.feedback_data["query_feedback"].append(feedback)
        self.save_feedback()
        
        self.logger.info(f"クエリへのフィードバックを追加しました: {query[:50]}...")
        
        # 個別のドキュメントフィードバックも追加
        for i, result in enumerate(results):
            if "metadata" in result and "chunk_id" in result["metadata"]:
                chunk_id = result["metadata"]["chunk_id"]
                # フィードバックのランクに応じた重み付け
                relevance = 0
                if rating >= 4:  # 良い評価
                    relevance = 5 - i  # 上位の結果ほど重み大
                elif rating <= 2:  # 悪い評価
                    relevance = -1  # 負の評価
                
                if relevance != 0:
                    self.add_document_feedback(chunk_id, query, relevance)
    
    def add_document_feedback(self, 
                             chunk_id: str, 
                             query_context: str, 
                             relevance: int):
        """
        特定のドキュメントチャンクに対するフィードバックを追加
        
        Args:
            chunk_id: ドキュメントチャンクのID
            query_context: 関連するクエリやコンテキスト
            relevance: 関連性スコア（正：関連あり、負：関連なし）
        """
        if chunk_id not in self.feedback_data["document_feedback"]:
            self.feedback_data["document_feedback"][chunk_id] = []
        
        feedback = {
            "query_context": query_context,
            "relevance": relevance,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.feedback_data["document_feedback"][chunk_id].append(feedback)
        self.save_feedback()
    
    def analyze_feedback(self) -> Dict[str, Any]:
        """
        フィードバックデータを分析してRAGエンジンの改善点を提案
        
        Returns:
            分析結果と改善提案
        """
        analysis = {
            "total_queries": len(self.feedback_data["query_feedback"]),
            "average_rating": 0,
            "top_positive_queries": [],
            "top_negative_queries": [],
            "most_relevant_documents": [],
            "least_relevant_documents": []
        }
        
        # 平均評価を計算
        if analysis["total_queries"] > 0:
            total_rating = sum(item["rating"] for item in self.feedback_data["query_feedback"])
            analysis["average_rating"] = total_rating / analysis["total_queries"]
        
        # クエリの評価によるソート
        sorted_queries = sorted(
            self.feedback_data["query_feedback"], 
            key=lambda x: x["rating"], 
            reverse=True
        )
        
        # 上位の良いクエリと悪いクエリを抽出
        analysis["top_positive_queries"] = [
            {"query": q["query"], "rating": q["rating"]}
            for q in sorted_queries[:5] if q["rating"] >= 4
        ]
        
        analysis["top_negative_queries"] = [
            {"query": q["query"], "rating": q["rating"]}
            for q in sorted_queries[-5:] if q["rating"] <= 2
        ]
        
        # ドキュメントの関連性を集計
        doc_relevance = {}
        for chunk_id, feedbacks in self.feedback_data["document_feedback"].items():
            total_relevance = sum(f["relevance"] for f in feedbacks)
            doc_relevance[chunk_id] = {
                "chunk_id": chunk_id,
                "total_relevance": total_relevance,
                "feedback_count": len(feedbacks)
            }
        
        # 関連性の高いドキュメントと低いドキュメントを抽出
        sorted_docs = sorted(
            doc_relevance.values(), 
            key=lambda x: x["total_relevance"], 
            reverse=True
        )
        
        analysis["most_relevant_documents"] = sorted_docs[:5]
        analysis["least_relevant_documents"] = sorted_docs[-5:]
        
        return analysis 