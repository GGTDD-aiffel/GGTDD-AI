import time
import logging
from typing import Any, Callable, TypeVar, Dict, Optional, cast
from functools import wraps

T = TypeVar('T')

class PerformanceTracker:
    def __init__(self, log_level: int = logging.INFO):
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(log_level)
        self.metrics: Dict[str, Dict[str, float]] = {}
        
        # 로그 핸들러 설정
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def measure(self, func: Callable[..., T], *args, **kwargs) -> T:
        """함수 실행 시간을 측정하고 결과 반환"""
        name = func.__name__
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        self._record_metric(name, "execution_time", elapsed_time)
        self.logger.info(f"{name} 실행 시간: {elapsed_time:.2f}초")
        
        return result
    
    def time_decorator(self, name: Optional[str] = None):
        """함수 실행 시간 측정 데코레이터"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            metric_name = name or func.__name__
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                
                self._record_metric(metric_name, "execution_time", elapsed_time)
                self.logger.info(f"{metric_name} 실행 시간: {elapsed_time:.2f}초")
                
                return result
            
            return cast(Callable[..., T], wrapper)
        return decorator
    
    def _record_metric(self, name: str, metric_type: str, value: float) -> None:
        """메트릭 기록"""
        if name not in self.metrics:
            self.metrics[name] = {}
        
        if metric_type not in self.metrics[name]:
            self.metrics[name][metric_type] = []
            
        self.metrics[name][metric_type].append(value)
    
    def get_avg_time(self, name: str) -> float:
        """특정 함수의 평균 실행 시간 반환"""
        if name in self.metrics and "execution_time" in self.metrics[name]:
            times = self.metrics[name]["execution_time"]
            return sum(times) / len(times)
        return 0.0
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """모든 측정 결과의 요약 정보 반환"""
        summary = {}
        
        for name, metrics in self.metrics.items():
            summary[name] = {}
            for metric_type, values in metrics.items():
                summary[name][f"avg_{metric_type}"] = sum(values) / len(values)
                summary[name][f"max_{metric_type}"] = max(values)
                summary[name][f"min_{metric_type}"] = min(values)
                summary[name][f"total_{metric_type}"] = sum(values)
                summary[name][f"count"] = len(values)
                
        return summary