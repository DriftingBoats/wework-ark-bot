#!/bin/bash

# WeWork Bot Linux 通用部署脚本
# 适用于所有 Linux 发行版的 Docker 部署方案

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
IMAGE_NAME="wework-bot"
CONTAINER_NAME="wework-bot"
PORT="5000"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测 Linux 发行版
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
        log_info "检测到系统: $PRETTY_NAME"
    else
        DISTRO="unknown"
        log_warning "无法检测系统版本，假设为通用 Linux"
    fi
}

# 检查系统环境
check_system() {
    log_info "检查系统环境..."
    
    detect_distro
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        echo "请根据你的系统安装 Docker:"
        echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y docker.io"
        echo "  CentOS/RHEL:   sudo yum install -y docker 或 sudo dnf install -y docker"
        echo "  Arch Linux:    sudo pacman -S docker"
        echo "  通用方法:      curl -fsSL https://get.docker.com | sh"
        echo ""
        echo "安装后请运行: sudo usermod -aG docker \$USER"
        echo "然后重新登录或运行: newgrp docker"
        exit 1
    fi
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行"
        echo "请启动 Docker 服务:"
        echo "  systemd 系统: sudo systemctl start docker && sudo systemctl enable docker"
        echo "  其他系统:     sudo service docker start"
        exit 1
    fi
    
    log_success "系统环境检查通过"
}

# 检查环境配置
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "已从 .env.example 复制配置文件"
            log_warning "请编辑 .env 文件配置必要的环境变量"
            echo "主要配置项："
            echo "  WEBHOOK_URL - 企业微信机器人Webhook地址"
            echo "  AMAP_API_KEY - 高德地图API密钥（可选）"
            echo "  TIANXING_API_KEY - 天行数据API密钥（可选）"
            read -p "是否现在编辑配置文件？(y/n): " edit_env
            if [ "$edit_env" = "y" ] || [ "$edit_env" = "Y" ]; then
                # 尝试使用不同的编辑器
                if command -v nano &> /dev/null; then
                    nano .env
                elif command -v vim &> /dev/null; then
                    vim .env
                elif command -v vi &> /dev/null; then
                    vi .env
                else
                    log_warning "未找到文本编辑器，请手动编辑 .env 文件"
                fi
            fi
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
}

# 构建镜像
build_image() {
    log_info "构建 Docker 镜像..."
    docker build -t $IMAGE_NAME:latest .
    log_success "镜像构建完成"
}

# 启动服务
start_service() {
    log_info "启动 WeWork Bot 服务..."
    
    # 停止已存在的容器
    if docker ps -a | grep -q $CONTAINER_NAME; then
        log_info "停止已存在的容器..."
        docker stop $CONTAINER_NAME || true
        docker rm $CONTAINER_NAME || true
    fi
    
    # 创建日志目录
    mkdir -p logs
    chmod 755 logs
    
    # 启动新容器
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p $PORT:5000 \
        -e TZ=Asia/Shanghai \
        --env-file .env \
        -v $(pwd)/logs:/app/logs \
        $IMAGE_NAME:latest
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker ps | grep -q $CONTAINER_NAME; then
        log_success "服务启动成功！"
        show_status
    else
        log_error "服务启动失败，请检查日志"
        docker logs $CONTAINER_NAME
        exit 1
    fi
}

# 停止服务
stop_service() {
    log_info "停止 WeWork Bot 服务..."
    docker stop $CONTAINER_NAME || true
    docker rm $CONTAINER_NAME || true
    log_success "服务已停止"
}

# 重启服务
restart_service() {
    log_info "重启 WeWork Bot 服务..."
    stop_service
    start_service
}

# 查看日志
show_logs() {
    log_info "显示服务日志..."
    docker logs -f --tail=100 $CONTAINER_NAME
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker ps | grep $CONTAINER_NAME || echo "容器未运行"
    
    # 检查健康状态
    if docker ps | grep -q "healthy"; then
        log_success "服务运行正常"
    elif docker ps | grep -q "unhealthy"; then
        log_warning "服务健康检查失败"
    fi
    
    # 显示访问地址
    if command -v hostname &> /dev/null; then
        local_ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    else
        local_ip="127.0.0.1"
    fi
    
    echo ""
    log_info "访问地址:"
    echo "  本地: http://localhost:$PORT"
    echo "  局域网: http://${local_ip}:$PORT"
    echo "  健康检查: http://localhost:$PORT/api/health"
    echo ""
}

# 设置开机自启动
setup_autostart() {
    log_info "设置开机自启动..."
    
    # 检查是否为systemd系统
    if ! command -v systemctl &> /dev/null; then
        log_error "此系统不支持systemd，无法设置开机自启动"
        return 1
    fi
    
    # 获取当前工作目录的绝对路径
    WORK_DIR=$(pwd)
    
    # 创建systemd服务文件
    cat > /tmp/wework-bot.service << EOF
[Unit]
Description=WeWork Bot Service
After=docker.service
Requires=docker.service

[Service]
Type=forking
User=root
WorkingDirectory=$WORK_DIR
ExecStart=$WORK_DIR/deploy.sh start
ExecStop=$WORK_DIR/deploy.sh stop
ExecReload=$WORK_DIR/deploy.sh restart
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 安装服务文件
    if sudo -n true 2>/dev/null; then
        sudo mv /tmp/wework-bot.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable wework-bot.service
        log_success "开机自启动设置完成"
        log_info "服务管理命令:"
        echo "  启动服务: sudo systemctl start wework-bot"
        echo "  停止服务: sudo systemctl stop wework-bot"
        echo "  查看状态: sudo systemctl status wework-bot"
        echo "  禁用自启: sudo systemctl disable wework-bot"
    else
        log_error "需要sudo权限来设置开机自启动"
        rm -f /tmp/wework-bot.service
        return 1
    fi
}

# 移除开机自启动
remove_autostart() {
    log_info "移除开机自启动..."
    
    if ! command -v systemctl &> /dev/null; then
        log_error "此系统不支持systemd"
        return 1
    fi
    
    if sudo -n true 2>/dev/null; then
        # 停止并禁用服务
        sudo systemctl stop wework-bot.service 2>/dev/null || true
        sudo systemctl disable wework-bot.service 2>/dev/null || true
        
        # 删除服务文件
        sudo rm -f /etc/systemd/system/wework-bot.service
        sudo systemctl daemon-reload
        
        log_success "开机自启动已移除"
    else
        log_error "需要sudo权限来移除开机自启动"
        return 1
    fi
}

# 设置定时任务
setup_cron() {
    log_info "设置定时任务..."
    
    # 从环境变量读取cron表达式，如果没有设置则使用默认值
    CRON_SCHEDULE=${CRON_SCHEDULE:-"0 10 * * 1-5"}
    
    # 创建定时任务脚本
    cat > /tmp/wework-cron.sh << 'EOF'
#!/bin/bash
# WeWork Bot 定时发送脚本
curl -s -X POST http://localhost:5000/api/message/send-daily || echo "$(date): Failed to send daily message" >> /var/log/wework-bot-cron.log
EOF
    
    chmod +x /tmp/wework-cron.sh
    
    # 尝试移动到系统目录
    if [ -w "/usr/local/bin" ]; then
        mv /tmp/wework-cron.sh /usr/local/bin/wework-cron.sh
        CRON_SCRIPT="/usr/local/bin/wework-cron.sh"
    elif sudo -n true 2>/dev/null; then
        sudo mv /tmp/wework-cron.sh /usr/local/bin/wework-cron.sh
        CRON_SCRIPT="/usr/local/bin/wework-cron.sh"
    else
        # 如果没有权限，放在用户目录
        mv /tmp/wework-cron.sh ~/wework-cron.sh
        CRON_SCRIPT="~/wework-cron.sh"
        log_warning "没有系统权限，脚本已放置在用户目录: ~/wework-cron.sh"
    fi
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_SCRIPT") | crontab -
    
    log_success "定时任务设置完成（时间: $CRON_SCHEDULE）"
    log_info "可以使用 'crontab -l' 查看定时任务"
}

# 更新服务
update_service() {
    log_info "更新 WeWork Bot 服务..."
    
    # 如果是git仓库，拉取最新代码
    if [ -d ".git" ]; then
        log_info "拉取最新代码..."
        git pull
    fi
    
    # 重新构建镜像
    build_image
    
    # 重启服务
    restart_service
    
    log_success "服务更新完成！"
}

# 清理资源
cleanup() {
    log_info "清理 Docker 资源..."
    
    # 停止并删除容器
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # 删除镜像
    docker rmi $IMAGE_NAME:latest 2>/dev/null || true
    
    # 清理未使用的镜像
    docker image prune -f
    
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "WeWork Bot Linux 通用部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  build         构建 Docker 镜像"
    echo "  start         启动服务"
    echo "  stop          停止服务"
    echo "  restart       重启服务"
    echo "  update        更新服务（重新构建并重启）"
    echo "  logs          查看日志"
    echo "  status        查看状态"
    echo "  install-cron  设置定时任务"
    echo "  autostart     设置开机自启动"
    echo "  remove-autostart 移除开机自启动"
    echo "  cleanup       清理资源"
    echo "  help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build         # 构建镜像"
    echo "  $0 start         # 启动服务"
    echo "  $0 update        # 更新服务"
    echo "  $0 logs          # 查看日志"
    echo "  $0 install-cron  # 设置定时任务"
    echo "  $0 autostart     # 设置开机自启动"
    echo ""
    echo "支持的 Linux 发行版:"
    echo "  - Ubuntu/Debian"
    echo "  - CentOS/RHEL/Fedora"
    echo "  - Arch Linux"
    echo "  - openSUSE"
    echo "  - Alpine Linux"
    echo "  - 其他支持 Docker 的 Linux 发行版"
    echo ""
}

# 主函数
main() {
    check_system
    
    case "${1:-help}" in
        build)
            check_env
            build_image
            ;;
        start)
            check_env
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        install-cron|cron)
            setup_cron
            ;;
        autostart)
            setup_autostart
            ;;
        remove-autostart)
            remove_autostart
            ;;
        update)
            check_env
            update_service
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"