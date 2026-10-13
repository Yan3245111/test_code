/*
二进制信号量
只有两个值：0 和 1
用于任务同步（一个任务等待另一个任务或中断发出信号）
可以跨任务释放（不要求同一任务获取和释放
*/ 

SemaphoreHandle_t xDataReadySemaphore;

// 中断服务函数
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    // 通知任务数据已接收
    xSemaphoreGiveFromISR(xDataReadySemaphore, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 数据处理任务
void vDataProcessTask(void *pvParameters) {
    while(1) {
        // 等待数据到达（阻塞）
        if (xSemaphoreTake(xDataReadySemaphore, portMAX_DELAY) == pdTRUE) {
            // 数据已就绪，处理数据
            ProcessUARTData();
        }
    }
}

void main(void) {
    xDataReadySemaphore = xSemaphoreCreateBinary();
    xTaskCreate(vDataProcessTask, "Process", 1000, NULL, 2, NULL);
    // 启动UART接收中断...
}
