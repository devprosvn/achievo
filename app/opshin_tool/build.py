
"""
OpShin Contract Build Tool
"""

import subprocess
import json
import os
from pathlib import Path


class OpShinBuilder:
    """Builder cho OpShin smart contracts"""
    
    def __init__(self, contract_dir: str = "app/contract"):
        self.contract_dir = Path(contract_dir)
        self.build_dir = Path("build")
        self.build_dir.mkdir(exist_ok=True)
    
    def compile_contract(self, contract_name: str) -> dict:
        """Compile OpShin contract to Plutus Core"""
        contract_path = self.contract_dir / f"{contract_name}.py"
        
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract {contract_name} not found")
        
        try:
            # Run OpShin compiler
            result = subprocess.run([
                "opshin", "compile",
                str(contract_path),
                "--output-dir", str(self.build_dir)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Compilation failed: {result.stderr}")
            
            # Read compiled contract
            plutus_file = self.build_dir / f"{contract_name}.plutus"
            with open(plutus_file, 'r') as f:
                plutus_core = json.load(f)
            
            return {
                "success": True,
                "plutus_core": plutus_core,
                "contract_size": len(json.dumps(plutus_core))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_contract(self, contract_name: str) -> dict:
        """Test OpShin contract"""
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                f"tests/contract/test_{contract_name}.py",
                "-v"
            ], capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    builder = OpShinBuilder()
    
    # Compile certificate contract
    result = builder.compile_contract("cert_nft")
    
    if result["success"]:
        print("✅ Contract compiled successfully")
        print(f"Contract size: {result['contract_size']} bytes")
    else:
        print("❌ Compilation failed:")
        print(result["error"])
