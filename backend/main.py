from gpu_m import read_gpu
import json


def main():
    # get GPU metrics
    metrics=read_gpu()
    
    if metrics is None:
        print("failed to read gpu metrics")
        return
    
    print("=" * 60)
    print(f"GPU: {metrics.gpu_name}")
    print("=" * 60)
    print(f"GPU Utilization:    {metrics.gpu_util}%")
    print(f"Memory Utilization: {metrics.mem_util}%")
    print(f"Memory Used:        {metrics.mem_used_mb} MB / {metrics.mem_total_mb} MB ({metrics.mem_pct}%)")
    print(f"Temperature:        {metrics.temperature}°C")
    print(f"Power Draw:         {metrics.power_draw}W / {metrics.power_limit}W ({metrics.power_pct}%)")
    print(f"Throttle Reason:    {metrics.throttle_reason}")
    print(f"Timestamp:          {metrics.timestamp}")
    print("=" * 60)
    
    print("\nJSON format:")
    print(json.dumps(metrics.to_dict(), indent=2))


if __name__ == "__main__":
    main()
