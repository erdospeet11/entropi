# MicroLLM Text Adventure

- **Micro-LLM Text-Based Adventure Game:** A low-latency interactive fiction engine driven by a fine-tuned 1B–3B parameter LLM for dynamic story narration, choice parsing, and game state updates.
- **Text-Driven & LLM-Generated Gameplay:** Model outputs structured responses (narration, story choices, state deltas) guided by modular genre system prompts and deterministic RAG (vector database) lookups for fixed lore anchors and world canon.
- **Visual Integration:** Reactive UI/rendering pipeline that maps LLM-generated visual keys to pre-rendered asset banks, procedural shaders (scanlines, film grain, vignette), and genre-specific visual themes.
- **Infrastructure & Deployment:** Full-stack architecture featuring containerized backend orchestrators (FastAPI/Go), optimized inference runners (vLLM / llama.cpp GGUF), embedded vector storage (ChromaDB/LanceDB), Terraform IaC, and automated CI/CD workflows.
- **Fine-Tuned Model:** Base model optimized for low token count footprints, strict JSON/structured delimiter outputs, and genre-specific tone adaptability using on-the-fly LoRA adapters.

## Run

You need Python 3, Node.js, and a browser with WebGPU (current Chrome or Edge).

From the repo root, once:

```bash
chmod +x dev.sh
```

Then start the API and the site together:

```bash
./dev.sh
```

The first run creates `.venv`, installs the Python packages, and runs `npm install` in `frontend/`. Later runs only start the two servers. Stop them with Ctrl+C.

- Site: http://localhost:5173/
- API: http://127.0.0.1:8000/

Opening the site loads `Llama-3.2-1B-Instruct-q4f16_1-MLC` in the browser and asks it for a greeting. Download progress and the reply are printed in the browser developer console. The weights are fetched on first use and cached in the browser; they are not in this repository. The API on port 8000 is separate and does not run the model.
