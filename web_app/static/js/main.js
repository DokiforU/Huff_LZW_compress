// web_app/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // 获取 DOM 元素
    const algoHuffmanRadio = document.getElementById('algoHuffman');
    const algoLzwRadio = document.getElementById('algoLzw');
    const modeCompressRadio = document.getElementById('modeCompress');
    const modeDecompressRadio = document.getElementById('modeDecompress');
    const fileInput = document.getElementById('fileInput');
    const processButton = document.getElementById('processButton');
    const statusArea = document.getElementById('statusArea');
    const errorArea = document.getElementById('errorArea');
    const resultsArea = document.getElementById('resultsArea');
    const metricsList = document.getElementById('metricsList'); // 获取ID
    const downloadLinkContainer = document.getElementById('downloadLinkContainer');
    const dropZone = document.getElementById('dropZone');
    const clearButton = document.getElementById('clearButton');
    const fileNameDisplay = document.getElementById('fileNameDisplay');

    // 检查 metricsList 是否成功获取
    console.log(">>> JS: DOM Loaded. Checking element 'metricsList':", metricsList);
    if (!metricsList) {
        console.error(">>> JS: CRITICAL - Element with ID 'metricsList' not found!");
    }
    // 检查 fileNameDisplay 是否成功获取
    console.log(">>> JS: DOM Loaded. Checking element 'fileNameDisplay':", fileNameDisplay);
     if (!fileNameDisplay) {
        console.error(">>> JS: CRITICAL - Element with ID 'fileNameDisplay' not found!");
    }


    // --- 事件监听 ---
    processButton.addEventListener('click', handleProcessRequest);
    clearButton.addEventListener('click', handleClearInput);

    algoHuffmanRadio.addEventListener('change', updateButtonText);
    algoLzwRadio.addEventListener('change', updateButtonText);
    modeCompressRadio.addEventListener('change', updateButtonText);
    modeDecompressRadio.addEventListener('change', updateButtonText);
    updateButtonText();

    // 文件输入变化时显示文件名
    fileInput.addEventListener('change', () => {
        console.log(">>> JS: fileInput change event fired."); // 确认事件触发
        displaySelectedFileName(fileInput.files);
    });

    // --- 拖拽功能 ---
    if (dropZone) {
        console.log(">>> JS: Adding drag/drop listeners to dropZone.");
        dropZone.addEventListener('dragenter', handleDragEnter, false);
        dropZone.addEventListener('dragover', handleDragOver, false);
        dropZone.addEventListener('dragleave', handleDragLeave, false);
        dropZone.addEventListener('drop', handleDrop, false);
        dropZone.addEventListener('click', (e) => {
            if (e.target.tagName !== 'LABEL' && e.target.tagName !== 'INPUT' && e.target.id !== 'fileInput' ) {
                 console.log(">>> JS: DropZone clicked, triggering file input.");
                 fileInput.click();
            }
        });
    } else { console.error(">>> JS: Drop zone element not found!"); }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        // console.log(`>>> JS: preventDefaults called for type: ${e.type}`);
        e.preventDefault();
        e.stopPropagation();
    }
    function handleDragEnter(e) { preventDefaults(e); dropZone.classList.add('dragover'); }
    function handleDragOver(e) { preventDefaults(e); dropZone.classList.add('dragover'); e.dataTransfer.dropEffect = 'copy'; }
    function handleDragLeave(e) { preventDefaults(e); dropZone.classList.remove('dragover'); }
    function handleDrop(e) {
        console.log(">>> JS: handleDrop function START");
        preventDefaults(e);
        dropZone.classList.remove('dragover');
        const dt = e.dataTransfer;
        const files = dt.files;
        console.log(`>>> JS: Files dropped: ${files.length}`);
        if (files.length > 0) {
            fileInput.files = files; // <--- 关键：将拖拽文件赋值给隐藏的input
            displaySelectedFileName(files); // 调用显示函数
            console.log(">>> JS: Dropped files assigned to fileInput and displayed.");
        }
        console.log(">>> JS: handleDrop function END");
     }
    // --- 拖拽功能结束 ---

    // --- 函数定义 ---
    function updateButtonText() { /* ... (不变) ... */ }
    function formatBytes(bytes, decimals = 2) {
        // 检查输入是否为有效数字，若无效则返回 'N/A'
        if (typeof bytes !== 'number' || isNaN(bytes)) return 'N/A';
        // 处理 0 的情况
        if (bytes === 0) return '0 Bytes';
        // 对于小于 1024 字节的值，直接返回字节数
        if (bytes < 1024) return `${bytes} Bytes`;
        // 对于大于等于 1024 字节的值，计算合适的单位
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // 显示选中的文件名 (增加日志)
    function displaySelectedFileName(files) {
         console.log(">>> JS: displaySelectedFileName called with files:", files);
         if (!fileNameDisplay) { // 再次检查确保元素存在
              console.error(">>> JS: fileNameDisplay element is null inside displaySelectedFileName!");
              return;
         }
         if (files && files.length > 0) {
             fileNameDisplay.textContent = `已选择: ${files[0].name}`;
             fileNameDisplay.classList.remove('text-muted'); // 移除灰色提示样式
             fileNameDisplay.classList.add('selected'); // 可选：添加选中样式
             console.log(">>> JS: Displaying filename:", files[0].name);
         } else {
             fileNameDisplay.textContent = '(未选择文件)';
             fileNameDisplay.classList.add('text-muted'); // 恢复灰色提示样式
             fileNameDisplay.classList.remove('selected');
             console.log(">>> JS: Displaying '未选择文件'");
         }
    }
    displaySelectedFileName(null); // 初始化显示

    function handleClearInput() {
        fileInput.value = null;
        displaySelectedFileName(null);
        hideError();
        hideResults();
        console.log("Inputs cleared.");
    }
// 主要的处理函数 (修正 await 用法和错误处理)

    async function handleProcessRequest() {
        // 1. 获取用户输入、模式和算法 (不变)
        const selectedMode = document.querySelector('input[name="mode"]:checked')?.value;
        const selectedAlgorithm = document.querySelector('input[name="algorithm"]:checked')?.value;
        const file = fileInput.files[0];

        // 2. 基本验证 (不变)
        if (!selectedAlgorithm) { showError('请选择压缩算法!'); return; }
        if (!selectedMode) { showError('请选择操作模式！'); return; }
        if (!file) { showError('请选择一个文件或将文件拖拽到上方区域！'); return; }

        // 3. 准备 FormData (不变)
        const formData = new FormData();
        formData.append('algorithm', selectedAlgorithm);
        formData.append('mode', selectedMode);
        formData.append('file', file);

        // 4. 更新 UI
        console.log(">>> JS: Attempting to show loading indicator...");
        showLoading(true);
        hideError();
        hideResults();
        processButton.disabled = true;
        // 给浏览器渲染 spinner 的机会
        await new Promise(resolve => setTimeout(resolve, 0));
        console.log(">>> JS: Proceeding with fetch after brief delay.");

        // 5. 发送 Fetch 请求并处理响应
        try {
            console.log(">>> JS: Sending fetch request to /process");
            const response = await fetch('/process', { method: 'POST', body: formData });
            console.log(">>> JS: Fetch response received.", response);

            if (response.ok) { // HTTP 状态码 200-299
                let data;
                try {
                    data = await response.json(); // 尝试解析为 JSON
                    console.log(">>> JS: Parsed JSON data:", data);

                    if (data && data.status === 'success') {
                        console.log(">>> JS: Processing successful response.");
                        displayResults(data, selectedMode, selectedAlgorithm);
                    } else if (data && data.message) { // 后端返回了 {status: 'error', message: '...'}
                        console.log(">>> JS: Processing error response from backend (JSON).");
                        showError(data.message);
                    } else { // 收到 2xx 但 JSON 格式不对或 status 不对
                        console.log(">>> JS: Received success status but unexpected data format:", data);
                        showError('收到来自服务器的未知成功响应格式。');
                    }
                } catch (jsonError) { // 响应 OK 但无法解析为 JSON
                    console.error(">>> JS: Failed to parse JSON response:", jsonError);
                    let responseText = "(无法读取响应文本)";
                    try {
                        responseText = await response.text(); // 尝试读取原始文本
                        console.error(">>> JS: Response text:", responseText);
                    } catch (textError) {
                        console.error(">>> JS: Also failed to read response text:", textError);
                    }
                    showError(`服务器响应成功但格式无效。响应内容: ${responseText.substring(0, 100)}...`);
                }
            } else { // HTTP 状态码表示错误 (4xx, 5xx)
                let errorText = `(无法读取错误响应体)`;
                try {
                    errorText = await response.text(); // 尝试读取错误响应体
                } catch(e) {
                    console.error(">>> JS: Failed to read error response text:", e);
                }
                console.error(`>>> JS: Fetch failed with status ${response.status}`, errorText);
                let errorMessage = `处理失败 (HTTP ${response.status})`;
                try { // 尝试将错误文本解析为我们后端定义的 JSON 错误
                    const errorJson = JSON.parse(errorText);
                    if (errorJson && errorJson.message) {
                        errorMessage = errorJson.message; // 使用后端提供的具体错误
                    } else {
                         errorMessage = errorText.substring(0, 150) || errorMessage; // 显示部分文本或通用HTTP错误
                    }
                } catch (e) { // 解析 JSON 失败，直接显示部分文本
                     errorMessage = errorText.substring(0, 150) || errorMessage;
                }
                showError(errorMessage);
            }

        } catch (networkError) { // 网络层面的错误 (e.g., DNS, connection refused)
            console.error('>>> JS: Fetch Network Error caught:', networkError);
            showError('请求失败，可能是网络问题或服务器无响应。');

        } finally { // 无论成功或失败，最终都执行
            console.log(">>> JS: Fetch finished (in finally block). Hiding loading, enabling button.");
            showLoading(false);
            processButton.disabled = false;
        }
    } // 结束 handleProcessRequest

    // UI 更新函数 (保持不变)
    function showLoading(isLoading) { console.log(`>>> JS: Setting loading indicator to: ${isLoading}`); statusArea.style.display = isLoading ? 'block' : 'none'; }
    function showError(message) { errorArea.textContent = `错误: ${message}`; errorArea.style.display = 'block'; hideResults(); }
    function hideError() { errorArea.style.display = 'none'; errorArea.textContent = ''; }
    function hideResults() { resultsArea.style.display = 'none'; if(metricsList) metricsList.innerHTML = ''; if(downloadLinkContainer) downloadLinkContainer.innerHTML = ''; } // 增加null检查

    // displayResults 函数 (最终修正模板字符串语法)
    function displayResults(data, mode, algorithm) {
        console.log(">>> JS: displayResults - START. Data received:", data);
        // 再次确认 metricsList 存在
        if (!metricsList) {
             console.error(">>> JS: displayResults - metricsList is null! Cannot update results.");
             showError("内部错误：无法显示结果区域。");
             return;
        }
        // 再次确认 downloadLinkContainer 存在
         if (!downloadLinkContainer) {
             console.error(">>> JS: displayResults - downloadLinkContainer is null! Cannot update results.");
             showError("内部错误：无法显示下载链接区域。");
             return;
        }


        try {
            metricsList.innerHTML = ''; // 清空旧指标
            downloadLinkContainer.innerHTML = ''; // 清空旧下载链接
            console.log(">>> JS: displayResults - Areas cleared.");

            const metrics = data.metrics;
            const algoName = algorithm === 'huffman' ? 'Huffman' : 'LZW';

            console.log(">>> JS: displayResults - Adding algorithm name:", algoName);
            // 使用正确的模板字符串
            metricsList.innerHTML += `<li>算法: <strong>${algoName}</strong></li>`;
            console.log(">>> JS: displayResults - Algorithm name added.");

            if (metrics) {
                console.log(">>> JS: displayResults - Processing metrics object:", metrics);
                try {
                    const time = metrics.time ?? 'N/A';
                    const originalSize = metrics.original_size ?? 'N/A'; // 获取原始值用于括号内显示
                    const finalSize = metrics.final_size ?? 'N/A'; // 获取原始值用于括号内显示
                    const ratio = metrics.ratio;

                    // --- 确保以下使用了正确的模板字符串和变量 ---
                    metricsList.innerHTML += `<li>处理耗时: ${time} 秒</li>`;
                    console.log(">>> JS: displayResults - Time added.");

                    metricsList.innerHTML += `<li>原始大小: ${formatBytes(originalSize)} (${originalSize} Bytes)</li>`; // 调用 formatBytes
                    console.log(">>> JS: displayResults - Original size added.");

                    metricsList.innerHTML += `<li>${mode === 'compress' ? '压缩后' : '解压后'}大小: ${formatBytes(finalSize)} (${finalSize} Bytes)</li>`; // 调用 formatBytes
                    console.log(">>> JS: displayResults - Final size added.");

                    if (mode === 'compress' && ratio !== null && ratio !== undefined) {
                        const ratioClass = ratio >= 0 ? 'text-success' : 'text-danger';
                        // 确保 class 属性和百分比显示正确
                        metricsList.innerHTML += `<li>压缩率: <strong class="${ratioClass}">${ratio}%</strong>${ratio < 0 ? ' (体积增大)' : ''}</li>`;
                        console.log(">>> JS: displayResults - Ratio added.");
                    } else {
                         console.log(">>> JS: displayResults - Skipping ratio display.");
                    }
                    console.log(">>> JS: displayResults - Metrics processing done.");

                } catch (metricsError) {
                    console.error(">>> JS: displayResults - Error while processing metrics:", metricsError);
                }
            } else {
                 console.log(">>> JS: displayResults - Metrics object not found in data.");
            }

            if (data.output_filename) {
                 console.log(">>> JS: displayResults - Creating download link for:", data.output_filename);
                try {
                    const downloadLink = document.createElement('a');
                    downloadLink.href = `/download/${encodeURIComponent(data.output_filename)}`;
                    downloadLink.textContent = `下载 (${algoName} ${mode === 'compress' ? '压缩' : '解压'}) 结果文件`;
                    downloadLink.className = 'btn btn-success mt-3';
                    console.log(">>> JS: displayResults - Appending download link...");
                    downloadLinkContainer.appendChild(downloadLink);
                    console.log(">>> JS: displayResults - Download link appended.");
                } catch(linkError) {
                     console.error(">>> JS: displayResults - Error creating/appending download link:", linkError);
                }
            } else {
                 console.log(">>> JS: displayResults - output_filename not found in data.");
            }

            console.log(">>> JS: displayResults - Making results area visible.");
            resultsArea.style.display = 'block'; // 显示结果区域
            hideError(); // 隐藏错误信息
            console.log(">>> JS: displayResults - END");
        } catch (outerError) {
             console.error(">>> JS: displayResults - Unexpected outer error:", outerError);
             showError("更新结果显示时发生意外错误。");
        }
    } // 结束 displayResults

}); // 结束 DOMContentLoaded