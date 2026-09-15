import pandas as pd
from typing import List, Dict, Any
from logger_config import get_logger

logger = get_logger("data_processor")

class TabularDataProcessor:
    @staticmethod
    def transform_metadata_table(df: pd.DataFrame, entity_type: str, id_col: str) -> List[Dict[str, Any]]:
        logger.info(f"Transforming {entity_type} table with {df.shape[0]} entities into semantic documents.")
        documents = []
        columns = df.columns.tolist()
        
        for _, row in df.iterrows():
            narrative_elements = [f"{col}: {row[col]}" for col in columns if pd.notna(row[col])]
            row_text = " | ".join(narrative_elements)
            
            documents.append({
                "id": f"{entity_type}_{row[id_col]}",
                "text": f"{entity_type.capitalize()} Entity Profile -> {row_text}",
                "metadata": {"entity_type": entity_type, id_col: str(row[id_col])}
            })
        return documents

    @staticmethod
    def generate_schema_blueprint(datasets: Dict[str, pd.DataFrame]) -> str:
        logger.info("Compiling schema blueprint for relational data mapping.")
        blueprint = []
        
        for file_name, df in datasets.items():
            blueprint.append(f"Table Asset: {file_name}")
            blueprint.append(f"Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
            blueprint.append("Columns & Data Types:")
            for col in df.columns:
                blueprint.append(f" - {col} ({df[col].dtype})")
            blueprint.append("Sample Data Snippet:")
            blueprint.append(df.head(2).to_string())
            blueprint.append("-" * 40)
            
        return "\n".join(blueprint)
