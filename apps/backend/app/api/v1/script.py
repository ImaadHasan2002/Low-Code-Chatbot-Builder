from fastapi import APIRouter, Depends
from app.core.security import get_current_user, get_current_workspace
from app.core.config import Settings

settings = Settings()

router = APIRouter()

@router.post("/generate")
async def generate_script():
    script_template = f"""
        (function() {{
            const chatbotConfig = {{
                workspaceId: "66f000000000000000000000",
                wsEndpoint: "{settings.BACKEND_URL.replace('http', 'ws')}/api/v1/playground/chat",
                userId: "66f000000000000000000000",
                theme: "light", // Can be customized
                position: "bottom-right", // Can be customized
                launcher: true // Show chat launcher
            }};
            
            const script = document.createElement('script');
            script.src = "/chatbot.js";
            script.async = true;
            script.onload = function() {{
                window.initChatbot(chatbotConfig);
            }};
            document.head.appendChild(script);
        }})();
    """
    return {"script": script_template} 