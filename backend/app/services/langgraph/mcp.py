"""
MCP (Model Context Protocol) 集成模块
提供标准协议访问外部工具服务器的能力
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from app.core.config import settings
from app.core.logger import logger


# 尝试导入 MCP 相关库，如果失败则使用备用方案
try:
    from langchain_mcp import MCPToolkit
    from langchain_mcp.adapters.openapi import OpenAPIToolkit
    MCP_AVAILABLE = True
except ImportError:
    try:
        from langchain_mcp_adapters import MCPToolkit, OpenAPIToolkit
        MCP_AVAILABLE = True
    except ImportError:
        MCP_AVAILABLE = False
        logger.warning("MCP 依赖未安装，将使用本地工具替代")


class MCPIntegration:
    """MCP 工具集成管理器"""
    
    def __init__(self):
        self.tools = []
        self.mcp_clients = {}
    
    def load_mcp_tools(self, server_url: str, server_name: str) -> List:
        """
        从 MCP 服务器加载工具
        """
        if not MCP_AVAILABLE:
            logger.warning("MCP 不可用，跳过加载")
            return []
        
        try:
            toolkit = MCPToolkit.from_remote(server_url)
            tools = toolkit.get_tools()
            self.mcp_clients[server_name] = toolkit
            self.tools.extend(tools)
            logger.info(f"[MCP] 从 {server_url} 加载了 {len(tools)} 个工具")
            return tools
        except Exception as e:
            logger.error(f"[MCP] 加载工具失败: {e}")
            return []
    
    def load_openapi_tools(self, spec_url: str, server_name: str) -> List:
        """
        从 OpenAPI 规范加载工具
        """
        if not MCP_AVAILABLE:
            logger.warning("MCP 不可用，跳过加载")
            return []
        
        try:
            toolkit = OpenAPIToolkit.from_remote(spec_url)
            tools = toolkit.get_tools()
            self.mcp_clients[server_name] = toolkit
            self.tools.extend(tools)
            logger.info(f"[MCP] 从 OpenAPI {spec_url} 加载了 {len(tools)} 个工具")
            return tools
        except Exception as e:
            logger.error(f"[MCP] 加载 OpenAPI 工具失败: {e}")
            return []
    
    def get_all_tools(self) -> List:
        """获取所有已加载的 MCP 工具"""
        return self.tools


mcp_integration = MCPIntegration()


def initialize_mcp():
    """初始化 MCP 工具集成"""
    logger.info("[MCP] 初始化 MCP 集成")
    
    internal_api_url = f"http://localhost:{settings.PORT}/openapi.json"
    
    try:
        mcp_integration.load_openapi_tools(internal_api_url, "internal_api")
    except Exception as e:
        logger.warning(f"[MCP] 加载内部 API 失败（可能服务尚未启动）: {e}")


@tool
async def weather_query(city: str) -> Dict[str, Any]:
    """
    查询城市天气（示例 MCP 工具）
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息
    """
    return {
        "city": city,
        "temperature": 25,
        "weather": "晴",
        "humidity": 60,
        "wind": "东北风 3级",
        "description": f"{city} 当前天气晴朗，温度适宜",
    }


@tool
async def logistics_tracking(tracking_number: str) -> Dict[str, Any]:
    """
    查询物流轨迹（示例 MCP 工具）
    
    Args:
        tracking_number: 物流单号
    
    Returns:
        物流轨迹信息
    """
    return {
        "tracking_number": tracking_number,
        "status": "运输中",
        "current_location": "上海市浦东新区",
        "estimated_delivery": "2026-06-30",
        "history": [
            {"time": "2026-06-28 09:00", "status": "已揽收"},
            {"time": "2026-06-28 14:00", "status": "已发出"},
            {"time": "2026-06-28 20:00", "status": "到达上海"},
        ],
    }


def get_fallback_tools() -> List:
    """获取备用工具（当 MCP 不可用时使用）"""
    return [weather_query, logistics_tracking]
