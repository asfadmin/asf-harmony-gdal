from dataclasses import dataclass

@dataclass
class Layer:
    layer_id: str
    filename: str
    output_dir: str

