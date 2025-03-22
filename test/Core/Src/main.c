/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2025 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
uint8_t u1_Receive[20];
uint8_t u3_Receive[6];
uint8_t u3_Transmit[3] = { 16, 2, 3 };
uint8_t number = 9;
uint8_t full[4] = { 0, 0, 0, 0 };

//电机3200次翻转一周
//顺时针0123垃圾桶，1是可回收
//上面1480平
//1240可倒0、2(1690倒0，1260倒2)  0右上角，1右下角
//1790可倒1、3(1663倒3，1300倒1)
//1520斜着可抓入
//顺时针转红外时间变长
//上挡板1550关1200开
//右挡板1360关1000开
//下挡板1250关950开
//左边挡板1400闭1150开
//1680升起914放下
//1865张开1346抓住
//右侧开门

//1电机youshang youshang为方向1，左下为0    0.0062304mm横向/格
//2电机zuoshang youxia为方向1，左上为0
//上下12808，左右17212

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
	if (GPIO_Pin == GPIO_PIN_12) {
		GPIO_PinState state = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_12);
		if (state == GPIO_PIN_SET) {
			full[0] = 1;
		}
		if (state == GPIO_PIN_RESET) {
			full[0] = 0;
		}
	}
	if (GPIO_Pin == GPIO_PIN_13) {
		GPIO_PinState state = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_13);
		if (state == GPIO_PIN_SET) {
			full[1] = 2;
		}
		if (state == GPIO_PIN_RESET) {
			full[1] = 0;
		}
	}
	if (GPIO_Pin == GPIO_PIN_14) {
		GPIO_PinState state = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_14);
		if (state == GPIO_PIN_SET) {
			full[2] = 4;
		}
		if (state == GPIO_PIN_RESET) {
			full[2] = 0;
		}
	}
	if (GPIO_Pin == GPIO_PIN_15) {
		GPIO_PinState state = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_15);
		if (state == GPIO_PIN_SET) {
			full[3] = 8;
		}
		if (state == GPIO_PIN_RESET) {
			full[3] = 0;
		}
	}
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	if (huart == &huart1) {
		HAL_UART_Receive_DMA(&huart1, u1_Receive, 5);
		for (int i = 0; i < 6; i++) {
			u1_printf("%d ", u1_Receive[i]);
		}
		int value = 1000 * (u1_Receive[1] - '0') + 100 * (u1_Receive[2] - '0')
				+ 10 * (u1_Receive[3] - '0') + u1_Receive[4] - '0';
		u1_printf("\nvalue=%d\n", value);
		switch (u1_Receive[0] - '0') {
		case 1:
			__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, value);
			break;
		case 2:
			__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, value);
			break;
		case 3:
			__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_3, value);
			break;
		case 4:
			__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_4, value);
			break;
		case 5:
			__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_1, value);
			break;
		case 6:
			__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_2, value);
			break;
		case 7:
			__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_3, value);
			break;
		case 8:
			__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_4, value);
			break;
		}
	}
	if (huart == &huart3) {
		u1_printf("\nreceive from huart3: ");
		for (int i = 0; i < 6; i++) {
			u1_printf("%d ", u3_Receive[i]);
		}
		HAL_UART_Receive_DMA(&huart3, u3_Receive, 6);
//		u3_Transmit[0] = 32;
//		HAL_UART_Transmit(&huart3, u3_Transmit, 1, HAL_MAX_DELAY);
		number = u3_Receive[4];
	}
}
void IsBoardOpen(uint8_t open) {
	if (open == 1) {
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_1, 1200);
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_2, 1000);
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_3, 950);
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_4, 1150);
	}
	if (open == 0) {
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_1, 1550);
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_2, 1360);
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_3, 1250);
		__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_4, 1400);
	}
	HAL_Delay(500);
}
void Pour(uint8_t num) {
	switch (num) {
	case 0:
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1240);
		HAL_Delay(1000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1690);
		HAL_Delay(2000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
		HAL_Delay(500);
		break;
	case 1:
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1790);
		HAL_Delay(1000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1260);
		HAL_Delay(2000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
		HAL_Delay(500);
		break;
	case 2:
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1240);
		HAL_Delay(1000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1260);
		HAL_Delay(2000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
		HAL_Delay(500);
		break;
	case 3:
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1790);
		HAL_Delay(1000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1690);
		HAL_Delay(2000);
		__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
		HAL_Delay(500);
		break;
	}
}
void Positon(int x, int y) {

}
void Catch() {
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_3, 1100);
	HAL_Delay(500);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_3, 914);
	HAL_Delay(500);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_4, 1346);
	HAL_Delay(500);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_3, 1680);
	HAL_Delay(500);
}
void Throw() {
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_4, 1865);
}
void Direction(uint8_t num) {

}
void Press() {
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_10, GPIO_PIN_SET);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_11, GPIO_PIN_RESET);
	HAL_Delay(4000);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_10, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_11, GPIO_PIN_SET);
	HAL_Delay(4000);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_11, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_10, GPIO_PIN_RESET);
}
/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void) {
	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_DMA_Init();
	MX_USART1_UART_Init();
	MX_TIM1_Init();
	MX_TIM2_Init();
	MX_USART2_UART_Init();
	MX_USART3_UART_Init();
	MX_TIM3_Init();
	/* USER CODE BEGIN 2 */
	HAL_UART_Receive_DMA(&huart1, u1_Receive, 5);
	HAL_UART_Receive_DMA(&huart3, u3_Receive, 5);

	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);//平台倒
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);//平台上旋转
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_3);//爪子伸长
	HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_4);//爪子抓取
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);//上挡板
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);//右挡板
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);//下挡板
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_4);//左挡板

	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1240);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1480);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_3, 1680);
	__HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_4, 1865);
	IsBoardOpen(0);

	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_10, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_11, GPIO_PIN_RESET);

	HAL_Delay(500); //                             归中心点
	Emm_V5_Pos_Control(2, 1, 5000, 0, 15130, 1, 0);
	HAL_Delay(500);
	Emm_V5_Pos_Control(1, 1, 5000, 0, 1690, 1, 0);
	HAL_Delay(500);


	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */

	while (1) {
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */
		if (number != 9 && number !=4) {
			IsBoardOpen(1);
			Pour(number);
			IsBoardOpen(0);
			GPIO_PinState state0 = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_12);
			if (state0 == GPIO_PIN_RESET) {
				full[0] = 1;
			}
			if (state0 == GPIO_PIN_SET) {
				full[0] = 0;
			}
			GPIO_PinState state1 = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_13);
			if (state1 == GPIO_PIN_RESET) {
				full[1] = 2;
			}
			if (state1 == GPIO_PIN_SET) {
				full[1] = 0;
			}
			GPIO_PinState state2 = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_14);
			if (state2 == GPIO_PIN_RESET) {
				full[2] = 4;
			}
			if (state2 == GPIO_PIN_SET) {
				full[2] = 0;
			}
			GPIO_PinState state3 = HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_15);
			if (state3 == GPIO_PIN_RESET) {
				full[3] = 8;
			}
			if (state3 == GPIO_PIN_SET) {
				full[3] = 0;
			}
			u3_Transmit[0] = 16 + full[0] + full[1] + full[2] + full[3];
			HAL_Delay(1000);
			HAL_UART_Transmit(&huart3, u3_Transmit, 1, HAL_MAX_DELAY);
			number = 9;
		}
		if (number ==4){
			Press();
			number=9;
		}
//	  IsBoardOpen(1);
//	  Pour(0);
//	  IsBoardOpen(0);
//	  HAL_Delay(2000);
//	  IsBoardOpen(1);
//	  Pour(1);
//	  IsBoardOpen(0);
//	  HAL_Delay(2000);
//	  Catch();
//	  HAL_Delay(2000);
//	  IsBoardOpen(1);
//	  Throw();
//	  IsBoardOpen(0);
//	  HAL_Delay(2000);

//	  Emm_V5_Pos_Control(1, 1, 5000, 0, 6400, 1, 1);
//	  HAL_Delay(10);
//	  Emm_V5_Pos_Control(2, 1, 5000, 0, 6400, 1, 1);//addr,dir,v,a,maichong,juedui,tongbu
//	  HAL_Delay(10);
//	  Emm_V5_Synchronous_motion(0);
//	  HAL_Delay(3000);
//	  Emm_V5_Pos_Control(1, 0, 5000, 0, 6400, 1, 1);
//	  HAL_Delay(10);
//	  Emm_V5_Pos_Control(2, 0, 5000, 0, 6400, 1, 1);
//	  HAL_Delay(10);
//	  Emm_V5_Synchronous_motion(0);
//	  HAL_Delay(3000);

//	  HAL_UART_Transmit(&huart3, u3_Transmit, 1, HAL_MAX_DELAY);
//	  HAL_Delay(2000);

//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1210);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1663);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1322);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_1, 1759);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1322);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1663);
//	  HAL_Delay(1500);
//	  __HAL_TIM_SetCompare(&htim2, TIM_CHANNEL_2, 1466);
//	  HAL_Delay(1500);

	}
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void) {
	RCC_OscInitTypeDef RCC_OscInitStruct = { 0 };
	RCC_ClkInitTypeDef RCC_ClkInitStruct = { 0 };

	/** Configure the main internal regulator output voltage
	 */
	__HAL_RCC_PWR_CLK_ENABLE();
	__HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
	RCC_OscInitStruct.HSIState = RCC_HSI_ON;
	RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
			| RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK) {
		Error_Handler();
	}
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void) {
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1) {
	}
	/* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
