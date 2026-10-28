# 基础镜像：Python 3.11（backlog 锁定版本）
FROM python:3.11-slim

WORKDIR /app

# 只装核心依赖（零依赖脚本也能跑，这里装可选的图像/校验增强）
COPY 06-scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝脚本 + 数据
COPY 06-scripts/ /app/scripts/
COPY 05-data-center/ /app/data/

# 数据校验是进入任何环节的前置门禁
ENTRYPOINT ["python", "scripts/validate_data.py"]
CMD ["all", "/app/data"]
