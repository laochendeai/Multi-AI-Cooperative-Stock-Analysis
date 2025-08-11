#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 报告处理模块
负责报告生成、导出和管理
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ReportHandler:
    """报告处理器"""
    
    def __init__(self, ui_instance):
        """初始化报告处理器"""
        self.ui = ui_instance
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # 支持的导出格式
        self.supported_formats = ["JSON", "TXT", "HTML", "MD"]
    
    def export_report(self, format_type, include_metadata=True):
        """导出报告"""
        if not self.ui.current_result:
            return "❌ 没有可导出的分析结果"
        
        if format_type not in self.supported_formats:
            return f"❌ 不支持的格式: {format_type}"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.{format_type.lower()}"
            filepath = self.reports_dir / filename
            
            # 准备报告内容
            report_content = self._prepare_report_content(include_metadata)
            
            # 根据格式导出
            if format_type == "JSON":
                self._export_json(filepath, report_content)
            elif format_type == "TXT":
                self._export_txt(filepath, report_content)
            elif format_type == "HTML":
                self._export_html(filepath, report_content)
            elif format_type == "MD":
                self._export_markdown(filepath, report_content)
            
            return f"✅ 报告已导出: {filename}"
            
        except Exception as e:
            return f"❌ 导出失败: {str(e)}"
    
    def _prepare_report_content(self, include_metadata=True):
        """准备报告内容"""
        content = {
            "analysis_result": str(self.ui.current_result),
            "timestamp": datetime.now().isoformat(),
        }
        
        if include_metadata:
            content.update({
                "system_info": self.ui.get_system_info(),
                "analysis_progress": self.ui.analysis_progress,
                "current_agent": self.ui.current_agent,
                "enhanced_features": self.ui.enhanced_features_available,
                "export_format": "详细报告"
            })
        
        return content
    
    def _export_json(self, filepath, content):
        """导出JSON格式"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    
    def _export_txt(self, filepath, content):
        """导出TXT格式"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("TradingAgents 股票分析报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"生成时间: {content['timestamp']}\n\n")
            
            if "system_info" in content:
                f.write("系统信息:\n")
                for key, value in content["system_info"].items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
            
            f.write("分析结果:\n")
            f.write("-" * 40 + "\n")
            f.write(content["analysis_result"])
            f.write("\n\n" + "=" * 60)
    
    def _export_html(self, filepath, content):
        """导出HTML格式"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradingAgents 分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .content {{ margin: 20px 0; }}
        .metadata {{ background: #e9e9e9; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .result {{ background: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 TradingAgents 股票分析报告</h1>
        <p>生成时间: {timestamp}</p>
    </div>
    
    {metadata_section}
    
    <div class="content">
        <h2>📊 分析结果</h2>
        <div class="result">
            <pre>{analysis_result}</pre>
        </div>
    </div>
</body>
</html>
        """
        
        metadata_section = ""
        if "system_info" in content:
            metadata_items = "\n".join([
                f"<p><strong>{k}:</strong> {v}</p>" 
                for k, v in content["system_info"].items()
            ])
            metadata_section = f"""
            <div class="metadata">
                <h3>🔧 系统信息</h3>
                {metadata_items}
            </div>
            """
        
        html_content = html_template.format(
            timestamp=content["timestamp"],
            metadata_section=metadata_section,
            analysis_result=content["analysis_result"]
        )
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def _export_markdown(self, filepath, content):
        """导出Markdown格式"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# 🤖 TradingAgents 股票分析报告\n\n")
            f.write(f"**生成时间**: {content['timestamp']}\n\n")
            
            if "system_info" in content:
                f.write("## 🔧 系统信息\n\n")
                for key, value in content["system_info"].items():
                    f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            f.write("## 📊 分析结果\n\n")
            f.write("```\n")
            f.write(content["analysis_result"])
            f.write("\n```\n\n")
            f.write("---\n")
            f.write("*报告由TradingAgents系统自动生成*")
    
    def list_reports(self):
        """列出所有报告"""
        try:
            reports = []
            for file_path in self.reports_dir.glob("analysis_report_*"):
                stat = file_path.stat()
                reports.append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                    "format": file_path.suffix[1:].upper()
                })
            
            # 按创建时间排序
            reports.sort(key=lambda x: x["created"], reverse=True)
            return reports
            
        except Exception as e:
            return f"❌ 获取报告列表失败: {str(e)}"
    
    def delete_report(self, filename):
        """删除报告"""
        try:
            filepath = self.reports_dir / filename
            if filepath.exists():
                filepath.unlink()
                return f"✅ 报告已删除: {filename}"
            else:
                return f"❌ 报告不存在: {filename}"
                
        except Exception as e:
            return f"❌ 删除失败: {str(e)}"
    
    def get_report_content(self, filename):
        """获取报告内容"""
        try:
            filepath = self.reports_dir / filename
            if not filepath.exists():
                return f"❌ 报告不存在: {filename}"
            
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
                
        except Exception as e:
            return f"❌ 读取失败: {str(e)}"
    
    def get_export_summary(self):
        """获取导出摘要"""
        reports = self.list_reports()
        if isinstance(reports, str):  # 错误信息
            return {"error": reports}
        
        total_size = sum(float(r["size"].split()[0]) for r in reports)
        format_count = {}
        for report in reports:
            fmt = report["format"]
            format_count[fmt] = format_count.get(fmt, 0) + 1
        
        return {
            "total_reports": len(reports),
            "total_size_kb": f"{total_size:.1f} KB",
            "format_distribution": format_count,
            "latest_report": reports[0] if reports else None
        }

def create_report_handler(ui_instance):
    """创建报告处理器"""
    return ReportHandler(ui_instance)
