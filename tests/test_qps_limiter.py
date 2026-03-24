"""Tests for QPSLimiter."""

import pytest
import time

from adp_cli.adp.qps_limiter import QPSLimiter
from adp_cli.adp.config import ConfigManager


def test_qps_limiter_init():
    """测试 QPS 限制器初始化。"""
    limiter = QPSLimiter()
    assert limiter.get_current_qps() == 1  # 默认免费用户


def test_get_current_qps():
    """测试获取当前 QPS。"""
    limiter = QPSLimiter()

    assert limiter.get_current_qps() == limiter.free_qps

    limiter.set_paid_user(True)
    assert limiter.get_current_qps() == limiter.paid_qps


def test_set_paid_user():
    """测试设置用户类型。"""
    limiter = QPSLimiter()

    assert limiter.is_paid is False
    assert limiter.get_current_qps() == 1

    limiter.set_paid_user(True)

    assert limiter.is_paid is True
    assert limiter.get_current_qps() == 2


def test_set_qps_limits():
    """测试设置 QPS 限制。"""
    limiter = QPSLimiter()

    limiter.set_qps_limits(5, 10)

    assert limiter.free_qps == 5
    assert limiter.paid_qps == 10


def test_acquire():
    """测试获取请求许可。"""
    limiter = QPSLimiter()
    limiter.set_qps_limits(10, 10)

    start_time = time.time()

    # 发送 10 个请求
    for _ in range(10):
        limiter.acquire()

    elapsed = time.time() - start_time

    # 应该大约 0.9-1.1 秒（10 个请求，每个间隔 0.1 秒）
    assert 0.0 < elapsed < 2.0


def test_acquire_with_limit():
    """测试带限制的请求许可获取。"""
    limiter = QPSLimiter()
    limiter.set_qps_limits(2, 2)  # 2 QPS

    start_time = time.time()

    # 发送 5 个请求
    for _ in range(5):
        limiter.acquire()

    elapsed = time.time() - start_time

    # 应该大约 2 秒（5 个请求，每个间隔 0.5 秒）
    assert 1.5 < elapsed < 3.0
