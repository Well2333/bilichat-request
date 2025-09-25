# 基于运行时基础镜像构建应用镜像
FROM well404/bilichat-request:runtime-latest

COPY ./src ./src
COPY ./pyproject.toml .
COPY ./README.md .
COPY ./start_server.py .
# 只安装项目本身为 editable，不安装依赖 (依赖已在运行时镜像中安装)
RUN pip install --no-cache-dir --no-deps -e .

HEALTHCHECK --interval=60s --timeout=2s --start-period=30s --retries=5 CMD curl -f http://localhost:40432/health || exit 1

CMD ["python", "start_server.py"]
