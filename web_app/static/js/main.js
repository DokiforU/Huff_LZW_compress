// web_app/static/js/main.js

// 全局声明变量
let fileInput, fileNameDisplay, customFileBtn, customFileName;

document.addEventListener('DOMContentLoaded', () => {
    // 在 DOM 加载后赋值
    fileInput = document.getElementById('fileInput');
    fileNameDisplay = document.getElementById('fileNameDisplay');
    customFileBtn = document.getElementById('customFileBtn');
    customFileName = document.getElementById('customFileName');
    // 获取 DOM 元素
    const algoHuffmanRadio = document.getElementById('algoHuffman');
    const algoLzwRadio = document.getElementById('algoLzw');
    const modeCompressRadio = document.getElementById('modeCompress');
    const modeDecompressRadio = document.getElementById('modeDecompress');
    const processButton = document.getElementById('processButton');
    const statusArea = document.getElementById('statusArea');
    const errorArea = document.getElementById('errorArea');
    const resultsArea = document.getElementById('resultsArea');
    const metricsList = document.getElementById('metricsList'); // 获取ID
    const downloadLinkContainer = document.getElementById('downloadLinkContainer');
    const dropZone = document.getElementById('dropZone');
    const clearButton = document.getElementById('clearButton');
    const welcomeArea = document.getElementById('welcomeArea');
    const progressBarContainer = document.getElementById('progressBarContainer');

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
        const files = fileInput.files;
        if (files.length > 0) {
            // 检查是否是目录
            const isDirectory = files[0].webkitRelativePath.split('/').length > 1;
            if (isDirectory) {
                // 显示目录名
                const dirName = files[0].webkitRelativePath.split('/')[0];
                displaySelectedFileName([{ name: dirName }]);
                // 设置目录标志
                fileInput.setAttribute('data-is-directory', 'true');
            } else {
                // 单个文件处理
                const file = files[0];
                displaySelectedFileName(files);
                // 清除目录标志
                fileInput.removeAttribute('data-is-directory');
            }
        } else {
            displaySelectedFileName(null);
            fileInput.removeAttribute('data-is-directory');
        }
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
            showToast(i18n[currentLang].dragDropInfo, 'info');
            // 自动触发处理流程（可选）
            // processButton.click();
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
        try {
            if (typeof customFileName === 'undefined' || !customFileName) return;
            // 调试输出
            console.log("files:", files);
            if (files && files.length > 0) {
                let isDirectory = false;
                for (let i = 0; i < files.length; i++) {
                    console.log(`file[${i}]: name=${files[i].name}, webkitRelativePath=${files[i].webkitRelativePath}`);
                    if (files[i].webkitRelativePath && files[i].webkitRelativePath.includes('/')) {
                        isDirectory = true;
                        break;
                    }
                }
                if (isDirectory || files.length > 1) {
                    customFileName.textContent = `${i18n[currentLang].selectedFilePrefix} 共${files.length}个文件`;
                    customFileName.classList.remove('empty');
                } else {
                    customFileName.textContent = `${i18n[currentLang].selectedFilePrefix} ${files[0].name}`;
                    customFileName.classList.remove('empty');
                }
            } else {
                customFileName.textContent = i18n[currentLang].noFileSelected;
                customFileName.classList.add('empty');
            }
        } catch (e) {
            console.error('displaySelectedFileName error:', e);
            return;
        }
    }
    displaySelectedFileName(null); // 初始化显示

    function handleClearInput() {
        fileInput.value = null;
        displaySelectedFileName(null);
        hideError();
        hideResults();
        showWelcome();
        // 新增：同步清空自定义文件名显示
        if (customFileName) {
            customFileName.textContent = i18n[currentLang].noFileSelected;
            customFileName.classList.add('empty');
        }
        console.log("Inputs cleared.");
    }

    let lastSelectedMode = null;
    let lastSelectedAlgorithm = null;

    let fakeProgress = 0;
    let fakeProgressTimer = null;
    let isProcessing = false;

    function startFakeProgress() {
        fakeProgress = 0;
        updateProgress(0);
        isProcessing = true;
        if (fakeProgressTimer) clearInterval(fakeProgressTimer);
        fakeProgressTimer = setInterval(() => {
            if (!isProcessing) return;
            if (fakeProgress < 80) {
                fakeProgress += Math.random() * 2 + 1; // 1~3%
            } else if (fakeProgress < 95) {
                fakeProgress += Math.random() * 0.7 + 0.3; // 0.3~1%
            } else if (fakeProgress < 99) {
                fakeProgress += Math.random() * 0.2 + 0.1; // 0.1~0.3%
            }
            if (fakeProgress > 99) fakeProgress = 99;
            updateProgress(Math.floor(fakeProgress));
        }, 120);
    }

    function finishFakeProgress() {
        isProcessing = false;
        if (fakeProgressTimer) clearInterval(fakeProgressTimer);
        updateProgress(100);
    }

    async function handleProcessRequest() {
        const selectedMode = document.querySelector('input[name="mode"]:checked')?.value;
        const selectedAlgorithm = document.querySelector('input[name="algorithm"]:checked')?.value;
        const files = fileInput.files;
        const isDirectory = fileInput.getAttribute('data-is-directory') === 'true';

        if (!selectedAlgorithm) { 
            showError(i18n[currentLang].selectAlgorithmError); 
            progressBarContainer.style.display = 'none';
            updateProgress(0);
            return; 
        }
        if (!selectedMode) { 
            showError(i18n[currentLang].selectModeError); 
            progressBarContainer.style.display = 'none';
            updateProgress(0);
            return; 
        }
        if (!files || files.length === 0) { 
            showError(i18n[currentLang].selectFileError); 
            progressBarContainer.style.display = 'none';
            updateProgress(0);
            return; 
        }

        // 文件后缀校验（仅对单个文件进行）
        if (!isDirectory && selectedMode === 'decompress') {
            const file = files[0];
            const fileExt = file.name.toLowerCase().split('.').pop();
            const expectedExt = selectedAlgorithm === 'huffman' ? 'huff' : 'lzw';
            // 允许.zip文件
            if (fileExt !== expectedExt && fileExt !== 'zip') {
                showError(i18n[currentLang].decompressFileTypeError.replace('{algo}', selectedAlgorithm === 'huffman' ? 'Huffman' : 'LZW').replace('{ext}', expectedExt));
                progressBarContainer.style.display = 'none';
                updateProgress(0);
                return;
            }
        }

        // 只有通过所有校验后再显示进度条和loading
        showLoading(true);
        hideError();
        hideResults();
        processButton.disabled = true;
        await new Promise(resolve => setTimeout(resolve, 0));
        progressBarContainer.style.display = 'block';
        updateProgress(0);
        startFakeProgress();

        try {
            const formData = new FormData();
            formData.append('algorithm', selectedAlgorithm);
            formData.append('mode', selectedMode);
            formData.append('is_directory', isDirectory.toString());
            
            // 如果是目录，需要创建一个ZIP文件
            if (isDirectory) {
                const zip = new JSZip();
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const relativePath = file.webkitRelativePath;
                    zip.file(relativePath, file);
                }
                const zipBlob = await zip.generateAsync({type: 'blob'});
                formData.append('file', zipBlob, 'directory.zip');
            } else {
                formData.append('file', files[0]);
            }

            const response = await fetch('/process', { method: 'POST', body: formData });
            if (response.ok) {
                let data = await response.json();
                finishFakeProgress(); // 处理完成，进度条到100%
                if (data && data.status === 'success') {
                    if (selectedMode === 'decompress' && data.file_list) {
                        renderFileList(data.file_list, data.session_id);
                        showResults();
                        return;
                    }
                    // 其余情况（压缩模式或无file_list），只显示压缩/解压结果
                    displayResults(data, selectedMode, selectedAlgorithm);
                    showResults();
                } else if (data && data.status === 'error') {
                    switch (data.error_type) {
                        case 'EncodingError':
                            showToast(data.message, 'warning');
                            break;
                        case 'FileTooLarge':
                            showToast(data.message, 'danger');
                            break;
                        case 'FormatError':
                            showError(data.message);
                            break;
                        case 'AlgorithmError':
                            showToast(data.message, 'danger');
                            break;
                        default:
                            showError(data.message);
                    }
                    progressBarContainer.style.display = 'none';
                    showWelcome();
                } else {
                    showError('收到来自服务器的未知成功响应格式。');
                    progressBarContainer.style.display = 'none';
                    showWelcome();
                }
                if (data.encoding_warning) {
                    showToast(data.encoding_warning, 'warning');
                }
            } else {
                finishFakeProgress();
                showError('请求失败，服务器无响应');
                progressBarContainer.style.display = 'none';
                showWelcome();
            }
        } catch (networkError) {
            finishFakeProgress();
            showError('网络错误，请检查连接');
            progressBarContainer.style.display = 'none';
            showWelcome();
        } finally {
            showLoading(false);
            processButton.disabled = false;
        }
    }

    // UI 更新函数 (保持不变)
    function showLoading(isLoading) { console.log(`>>> JS: Setting loading indicator to: ${isLoading}`); statusArea.style.display = isLoading ? 'block' : 'none'; }
    function showError(message) { errorArea.textContent = `错误: ${message}`; errorArea.style.display = 'block'; hideResults(); }
    function hideError() { errorArea.style.display = 'none'; errorArea.textContent = ''; }
    function hideResults() {
        if (resultsArea) resultsArea.style.display = 'none';
        if (downloadLinkContainer) downloadLinkContainer.innerHTML = '';
        if (metricsList) metricsList.innerHTML = '';
    }

    // displayResults 函数 (最终修正模板字符串语法)
    function displayResults(data, mode, algorithm) {
        console.log(">>> JS: displayResults - START. Data received:", data);
        // 再次确认 metricsList 存在
        if (!metricsList) {
             console.error(">>> JS: displayResults - metricsList is null! Cannot update results.");
             showError(i18n[currentLang].internalError);
             return;
        }
        // 再次确认 downloadLinkContainer 存在
         if (!downloadLinkContainer) {
             console.error(">>> JS: displayResults - downloadLinkContainer is null! Cannot update results.");
             showError(i18n[currentLang].internalError);
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
            metricsList.innerHTML += `<li>${i18n[currentLang].resultAlgorithm}: <strong>${algoName}</strong></li>`;
            console.log(">>> JS: displayResults - Algorithm name added.");

            if (metrics) {
                console.log(">>> JS: displayResults - Processing metrics object:", metrics);
                try {
                    const time = metrics.time ?? 'N/A';
                    const originalSize = metrics.original_size ?? 'N/A'; // 获取原始值用于括号内显示
                    const finalSize = metrics.final_size ?? 'N/A'; // 获取原始值用于括号内显示
                    const ratio = metrics.ratio;

                    metricsList.innerHTML += `<li>${i18n[currentLang].resultTime}: ${time} ${i18n[currentLang].resultSeconds}</li>`;
                    metricsList.innerHTML += `<li>${i18n[currentLang].resultOriginalSize}: ${formatBytes(originalSize)} (${originalSize} ${i18n[currentLang].resultBytes})</li>`;
                    metricsList.innerHTML += `<li>${mode === 'compress' ? i18n[currentLang].resultFinalSize : i18n[currentLang].resultDecompressedSize}: ${formatBytes(finalSize)} (${finalSize} ${i18n[currentLang].resultBytes})</li>`;

                    if (mode === 'compress' && ratio !== null && ratio !== undefined) {
                        const ratioClass = ratio >= 0 ? 'text-success' : 'text-danger highlight-ratio';
                        metricsList.innerHTML += `<li id="ratioLi">${i18n[currentLang].resultRatio}: <strong class="${ratioClass}">${ratio}%</strong>${ratio < 0 ? ' (体积增大)' : ''}</li>`;
                        // 新增：体积增大时弹窗警告
                        if (ratio < 0) {
                            showToast(i18n[currentLang].compressNegativeWarning, 'warning');
                            // 高亮压缩率
                            setTimeout(() => {
                                const ratioLi = document.getElementById('ratioLi');
                                if (ratioLi) {
                                    ratioLi.classList.add('highlight-flash');
                                    setTimeout(() => ratioLi.classList.remove('highlight-flash'), 2000);
                                }
                            }, 200);
                        }
                    }
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
                    downloadLink.textContent = i18n[currentLang].resultDownload.replace('{algo}', algoName).replace('{mode}', mode === 'compress' ? i18n[currentLang].compress : i18n[currentLang].decompress);
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

            resultsArea.style.display = 'block'; // 显示结果区域
            hideError(); // 隐藏错误信息
            resultsArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
            resultsArea.classList.add('highlight-flash');
            setTimeout(() => resultsArea.classList.remove('highlight-flash'), 1200);

            if (downloadLinkContainer.firstChild) {
                downloadLinkContainer.firstChild.focus();
                downloadLinkContainer.firstChild.classList.add('btn-warning');
                setTimeout(() => downloadLinkContainer.firstChild.classList.remove('btn-warning'), 800);
            }

            if (document.getElementById('resultTitle')) document.getElementById('resultTitle').textContent = i18n[currentLang].resultTitle;
        } catch (outerError) {
             console.error(">>> JS: displayResults - Unexpected outer error:", outerError);
             showError(i18n[currentLang].updateResultsError);
        }
    } // 结束 displayResults

    function updateProgress(percent) {
        const bar = document.getElementById('progressBar');
        bar.style.width = percent + '%';
        bar.textContent = percent + '%';
    }

    function showToast(message, type='danger') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0 show`;
        toast.role = 'alert';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // 页面初始显示欢迎卡片
    showWelcome();

    function showWelcome() {
        if (welcomeArea) welcomeArea.style.display = 'block';
        if (resultsArea) resultsArea.style.display = 'none';
        if (progressBarContainer) progressBarContainer.style.display = 'none';
        updateProgress(0);
    }
    function showResults() {
        if (welcomeArea) welcomeArea.style.display = 'none';
        if (resultsArea) resultsArea.style.display = 'block';
    }

    // 新增：渲染文件列表并支持多选下载
    function renderFileList(fileList, sessionId) {
        let html = '<form id="fileSelectForm" style="max-width:600px;margin:auto;">';
        html += '<div class="d-flex mb-2" style="gap:1em;">'
        html += '<button type="button" id="selectAllBtn" class="btn btn-outline-secondary btn-sm">全选</button>';
        html += '<button type="button" id="deselectAllBtn" class="btn btn-outline-secondary btn-sm">反选</button>';
        html += '</div>';
        html += '<ul style="list-style:none;padding-left:0;">';
        fileList.forEach(function(path, idx) {
            const fileName = path.split('/').pop();
            html += `<li style="display:flex;align-items:center;margin-bottom:0.7em;border-bottom:1px solid #e3eafc;padding:0.4em 0;">
                <input type='checkbox' name='file' value='${encodeURIComponent(path)}' id='file_${idx}' style="margin-right:0.7em;transform:scale(1.2);">
                <label for='file_${idx}' style="flex:1 1 0;min-width:0;word-break:break-all;white-space:normal;margin-bottom:0;">${fileName}</label>
                <a href="/download_single?path=${encodeURIComponent(path)}" target="_blank" class="btn btn-outline-primary btn-sm" style="margin-left:1em;white-space:nowrap;">下载</a>
            </li>`;
        });
        html += '</ul>';
        html += '<button type="button" id="downloadSelectedBtn" class="btn btn-primary mt-2">批量下载所选文件</button>';
        html += '</form>';
        document.getElementById('downloadLinkContainer').innerHTML = html;
        // 全选
        document.getElementById('selectAllBtn').onclick = function() {
            document.querySelectorAll('#fileSelectForm input[name="file"]').forEach(cb => cb.checked = true);
        };
        // 反选
        document.getElementById('deselectAllBtn').onclick = function() {
            document.querySelectorAll('#fileSelectForm input[name="file"]').forEach(cb => cb.checked = !cb.checked);
        };
        // 批量下载
        document.getElementById('downloadSelectedBtn').onclick = function() {
            const checked = Array.from(document.querySelectorAll('#fileSelectForm input[name="file"]:checked')).map(cb => decodeURIComponent(cb.value));
            if (checked.length === 0) { alert(i18n[currentLang].selectFileError); return; }
            fetch('/download_multi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths: checked })
            }).then(resp => resp.blob()).then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'selected_files.zip';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            });
        };
    }

    // 粘贴上传支持
    document.addEventListener('paste', function(e) {
        if (e.clipboardData && e.clipboardData.files && e.clipboardData.files.length > 0) {
            fileInput.files = e.clipboardData.files;
            displaySelectedFileName(e.clipboardData.files);
            showToast(i18n[currentLang].pasteInfo, 'info');
            // 自动触发处理流程（可选）
            // processButton.click();
        }
    });

    // 语言切换和夜间模式
    const langSwitchBtn = document.getElementById('langSwitchBtn');
    const darkModeBtn = document.getElementById('darkModeBtn');
    let currentLang = 'zh';
    let isDark = false;
    // 简单i18n字典
    const i18n = {
        zh: {
            help: '帮助',
            compress: '压缩',
            decompress: '解压缩',
            selectFile: '选择文件或文件夹：',
            selected: '已选择:',
            start: '开始处理',
            clear: '清空输入',
            tips: '提示：',
            algoHuffman: 'Huffman',
            algoLzw: 'LZW',
            modeCompress: '压缩',
            modeDecompress: '解压缩',
            download: '下载',
            selectAll: '全选',
            deselectAll: '反选',
            batchDownload: '批量下载所选文件',
            night: '🌙 夜间模式',
            day: '☀️ 日间模式',
            lang: 'English',
            selectAlgorithmError: '请选择压缩算法!',
            selectModeError: '请选择操作模式！',
            selectFileError: '请选择一个文件或将文件拖拽到上方区域！',
            decompressFileTypeError: '解压{algo}文件时，请上传.{ext}或.zip格式的文件',
            compressNegativeWarning: '警告：该文件压缩后体积反而变大，建议直接传输原文件。',
            internalError: '内部错误：无法显示结果区域。',
            updateResultsError: '更新结果显示时发生意外错误。',
            dragDropInfo: '已拖拽文件，准备上传',
            pasteInfo: '已粘贴文件，准备上传',
            pageTitle: '文件压缩与解压缩工具',
            title: '文件压缩与解压缩工具',
            algorithm: '算法',
            huffman: 'Huffman',
            lzw: 'LZW',
            mode: '模式',
            compress: '压缩',
            decompress: '解压缩',
            welcomeTitle: '欢迎使用文件压缩/解压缩工具',
            welcomeItem1: '支持 Huffman、LZW 算法，适合文本、图片、音频、视频、二进制等所有类型文件和文件夹。',
            welcomeItem2: '最大支持 20MB，支持任意格式（如 .txt .bin .dat .jpg .png .mp3 .mp4 .zip .huff .lzw 等）。',
            welcomeItem3: '压缩率、处理速度一目了然，结果可直接下载。',
            downloadExampleText: '下载示例文本',
            downloadExampleBin: '下载示例二进制',
            footerText: '版权所有 &copy; {year} 文件压缩与解压缩工具',
            helpTitle: '帮助与说明',
            helpUsage: '使用说明',
            helpUsage1: 'Huffman 对文本效果好，LZW 适合高重复二进制数据。',
            helpUsage2: '支持 .txt, .log, .csv, .xml, .htm, .html, .c, .cpp, .java, .py, .js, .sql, .json, .md, .bmp, .bin, .dat 等格式。',
            helpUsage3: '解压时请上传对应算法生成的压缩文件(.huff 或 .lzw)。',
            helpUsage4: '支持上传整个目录（会自动打包为ZIP文件）。',
            helpFAQ: '常见问题',
            helpQ1: '为什么有些文件解压后乱码？',
            helpA1: '可能是原文件编码不是UTF-8，建议用记事本另存为UTF-8格式。',
            helpQ2: '支持哪些文件类型？',
            helpA2: '支持文本、二进制、图片、代码等常见格式，目录会自动打包为ZIP。',
            helpQ3: '压缩率为什么有时为负？',
            helpA3: '随机或已压缩文件用Huffman/LZW可能体积反而变大。',
            helpAlgo: '算法原理简介',
            helpHuffman: 'Huffman编码：基于字符出现频率构建最优前缀树，适合文本压缩。',
            helpLZW: 'LZW算法：基于字典的无损压缩，适合高重复二进制数据。',
            helpMore: '如有更多问题请联系开发者或查阅项目文档。',
            noFileSelected: '(未选择文件)',
            dropTip: '拖拽或粘贴文件/文件夹到此处上传',
            resultTitle: '处理结果',
            resultAlgorithm: '算法',
            resultTime: '处理耗时',
            resultOriginalSize: '原始大小',
            resultFinalSize: '压缩后大小',
            resultDecompressedSize: '解压后大小',
            resultRatio: '压缩率',
            resultDownload: '下载（{algo} {mode}）结果文件',
            resultSeconds: '秒',
            resultBytes: '字节',
            fileInputLabel: '选择文件或文件夹：',
            selectedFilePrefix: '已选择：',
            selectFileBtn: '选择文件',
        },
        en: {
            help: 'Help',
            compress: 'Compress',
            decompress: 'Decompress',
            selectFile: 'Select File or Folder:',
            selected: 'Selected:',
            start: 'Start',
            clear: 'Clear',
            tips: 'Tips:',
            algoHuffman: 'Huffman',
            algoLzw: 'LZW',
            modeCompress: 'Compress',
            modeDecompress: 'Decompress',
            download: 'Download',
            selectAll: 'Select All',
            deselectAll: 'Deselect',
            batchDownload: 'Batch Download Selected',
            night: '🌙 Night Mode',
            day: '☀️ Day Mode',
            lang: '中文',
            selectAlgorithmError: '请选择压缩算法!',
            selectModeError: '请选择操作模式！',
            selectFileError: '请选择一个文件或将文件拖拽到上方区域！',
            decompressFileTypeError: '解压{algo}文件时，请上传.{ext}或.zip格式的文件',
            compressNegativeWarning: '警告：该文件压缩后体积反而变大，建议直接传输原文件。',
            internalError: '内部错误：无法显示结果区域。',
            updateResultsError: '更新结果显示时发生意外错误。',
            dragDropInfo: '已拖拽文件，准备上传',
            pasteInfo: '已粘贴文件，准备上传',
            pageTitle: 'File Compression and Decompression Tool',
            title: 'File Compression and Decompression Tool',
            algorithm: 'Algorithm',
            huffman: 'Huffman',
            lzw: 'LZW',
            mode: 'Mode',
            compress: 'Compress',
            decompress: 'Decompress',
            welcomeTitle: 'Welcome to the File Compression and Decompression Tool',
            welcomeItem1: 'Supports Huffman and LZW algorithms, suitable for all types of files and folders including text, images, audio, video, and binary.',
            welcomeItem2: 'Supports files up to 20MB and any format (e.g. .txt, .bin, .dat, .jpg, .png, .mp3, .mp4, .zip, .huff, .lzw, etc.).',
            welcomeItem3: 'Compression ratio and processing speed are clear at a glance, and results can be downloaded directly.',
            downloadExampleText: 'Download Example Text',
            downloadExampleBin: 'Download Example Binary',
            footerText: 'Copyright &copy; {year} File Compression and Decompression Tool',
            helpTitle: 'Help & Instructions',
            helpUsage: 'Usage',
            helpUsage1: 'Huffman works well for text, LZW is suitable for highly repetitive binary data.',
            helpUsage2: 'Supports .txt, .log, .csv, .xml, .htm, .html, .c, .cpp, .java, .py, .js, .sql, .json, .md, .bmp, .bin, .dat and more.',
            helpUsage3: 'When decompressing, please upload files generated by the corresponding algorithm (.huff or .lzw).',
            helpUsage4: 'Supports uploading entire directories (will be automatically packed into ZIP).',
            helpFAQ: 'FAQ',
            helpQ1: 'Why are some files garbled after decompression?',
            helpA1: 'The original file may not be UTF-8 encoded. Please save as UTF-8 with Notepad.',
            helpQ2: 'What file types are supported?',
            helpA2: 'Text, binary, images, code, etc. Directories are automatically packed as ZIP.',
            helpQ3: 'Why is the compression ratio sometimes negative?',
            helpA3: 'Random or already compressed files may become larger with Huffman/LZW.',
            helpAlgo: 'Algorithm Introduction',
            helpHuffman: 'Huffman Coding: Builds an optimal prefix tree based on character frequency, suitable for text compression.',
            helpLZW: 'LZW Algorithm: Dictionary-based lossless compression, suitable for highly repetitive binary data.',
            helpMore: 'For more questions, contact the developer or check the documentation.',
            noFileSelected: '(No file selected)',
            dropTip: 'Drag and drop files or folders here, or paste files',
            resultTitle: 'Result',
            resultAlgorithm: 'Algorithm',
            resultTime: 'Time',
            resultOriginalSize: 'Original Size',
            resultFinalSize: 'Compressed Size',
            resultDecompressedSize: 'Decompressed Size',
            resultRatio: 'Compression Ratio',
            resultDownload: 'Download ({algo} {mode}) Result File',
            resultSeconds: 's',
            resultBytes: 'Bytes',
            fileInputLabel: 'Select File or Folder:',
            selectedFilePrefix: 'Selected:',
            selectFileBtn: 'Select File',
        }
    };
    function switchLang() {
        currentLang = currentLang === 'zh' ? 'en' : 'zh';
        langSwitchBtn.textContent = i18n[currentLang].lang;
        // 示例：切换部分主要文本
        document.querySelector('.algo-select-label').textContent = i18n[currentLang].algoHuffman + ' / ' + i18n[currentLang].algoLzw;
        document.querySelector('.mode-select-label').textContent = i18n[currentLang].modeCompress + ' / ' + i18n[currentLang].modeDecompress;
        document.querySelector('label[for="fileInput"]').textContent = i18n[currentLang].selectFile;
        processButton.textContent = i18n[currentLang].start;
        clearButton.textContent = i18n[currentLang].clear;
        updateUILanguage();
    }
    langSwitchBtn.onclick = switchLang;

    function switchDarkMode() {
        const body = document.body;
        const isDarkMode = body.classList.toggle('dark-mode');
        const darkModeBtn = document.getElementById('darkModeBtn');
        
        // 更新按钮文本
        darkModeBtn.innerHTML = isDarkMode ? '☀️ 日间模式' : '🌙 夜间模式';
        
        // 保存用户偏好
        localStorage.setItem('darkMode', isDarkMode ? 'true' : 'false');
        
        // 更新所有相关元素的样式
        const mainPanel = document.querySelector('.main-panel');
        if (mainPanel) {
            if (isDarkMode) {
                mainPanel.classList.add('dark-mode');
            } else {
                mainPanel.classList.remove('dark-mode');
            }
        }
        updateUILanguage();
    }
    darkModeBtn.onclick = switchDarkMode;

    // 页面加载时检查用户偏好
    document.addEventListener('DOMContentLoaded', function() {
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.body.classList.add('dark-mode');
            const mainPanel = document.querySelector('.main-panel');
            if (mainPanel) {
                mainPanel.classList.add('dark-mode');
            }
            const darkModeBtn = document.getElementById('darkModeBtn');
            if (darkModeBtn) {
                darkModeBtn.innerHTML = '☀️ 日间模式';
            }
        }
    });

    // 夜间模式简单样式（可在css中扩展更丰富的深色主题）
    const darkStyle = document.createElement('style');
    darkStyle.innerHTML = `
    body.dark-mode, .dark-mode .main-panel {
        background: #23272f !important;
        color: #e0e0e0 !important;
    }
    .dark-mode .main-panel, .dark-mode .card-results, .dark-mode .card-welcome {
        background: #23272f !important;
        color: #e0e0e0 !important;
        border-color: #444 !important;
    }
    .dark-mode .btn, .dark-mode .btn-lg, .dark-mode .btn-outline-primary, .dark-mode .btn-outline-secondary {
        background: #23272f !important;
        color: #b6e6c6 !important;
        border-color: #444 !important;
    }
    .dark-mode .progress {
        background: #333 !important;
    }
    .dark-mode .progress-bar {
        background: linear-gradient(90deg, #38d39f 0%, #4f8cff 100%) !important;
        color: #fff;
    }
    .dark-mode .toast {
        background: #23272f !important;
        color: #e0e0e0 !important;
    }
    .dark-mode #dropZone {
        background: #23272f !important;
        border-color: #38d39f !important;
        color: #b6e6c6 !important;
    }
    `;
    document.head.appendChild(darkStyle);

    function updateUILanguage() {
        const lang = i18n[currentLang];
        document.title = lang.pageTitle;
        if (document.getElementById('mainTitle')) document.getElementById('mainTitle').textContent = lang.title;
        if (document.getElementById('algoLabel')) document.getElementById('algoLabel').textContent = lang.algorithm;
        if (document.getElementById('labelHuffman')) document.getElementById('labelHuffman').textContent = lang.huffman;
        if (document.getElementById('labelLzw')) document.getElementById('labelLzw').textContent = lang.lzw;
        if (document.getElementById('modeLabel')) document.getElementById('modeLabel').textContent = lang.mode;
        if (document.getElementById('labelCompress')) document.getElementById('labelCompress').textContent = lang.compress;
        if (document.getElementById('labelDecompress')) document.getElementById('labelDecompress').textContent = lang.decompress;
        if (document.getElementById('fileInputLabel')) document.getElementById('fileInputLabel').textContent = lang.fileInputLabel;
        if (document.getElementById('processButton')) document.getElementById('processButton').textContent = lang.start;
        if (document.getElementById('clearButton')) document.getElementById('clearButton').textContent = lang.clear;
        if (document.getElementById('welcomeTitle')) document.getElementById('welcomeTitle').textContent = lang.welcomeTitle;
        if (document.getElementById('welcomeItem1')) document.getElementById('welcomeItem1').textContent = lang.welcomeItem1;
        if (document.getElementById('welcomeItem2')) document.getElementById('welcomeItem2').textContent = lang.welcomeItem2;
        if (document.getElementById('welcomeItem3')) document.getElementById('welcomeItem3').textContent = lang.welcomeItem3;
        if (document.getElementById('downloadExampleText')) document.getElementById('downloadExampleText').textContent = lang.downloadExampleText;
        if (document.getElementById('downloadExampleBin')) document.getElementById('downloadExampleBin').textContent = lang.downloadExampleBin;
        if (document.getElementById('footerText')) document.getElementById('footerText').innerHTML = lang.footerText.replace('{year}', new Date().getFullYear());
        if (document.getElementById('helpModalLabel')) document.getElementById('helpModalLabel').textContent = lang.helpTitle;
        if (document.getElementById('helpUsageTitle')) document.getElementById('helpUsageTitle').textContent = lang.helpUsage;
        if (document.getElementById('helpUsage1')) document.getElementById('helpUsage1').textContent = lang.helpUsage1;
        if (document.getElementById('helpUsage2')) document.getElementById('helpUsage2').textContent = lang.helpUsage2;
        if (document.getElementById('helpUsage3')) document.getElementById('helpUsage3').textContent = lang.helpUsage3;
        if (document.getElementById('helpUsage4')) document.getElementById('helpUsage4').textContent = lang.helpUsage4;
        if (document.getElementById('helpFAQTitle')) document.getElementById('helpFAQTitle').textContent = lang.helpFAQ;
        if (document.getElementById('helpQ1')) document.getElementById('helpQ1').textContent = lang.helpQ1;
        if (document.getElementById('helpA1')) document.getElementById('helpA1').textContent = lang.helpA1;
        if (document.getElementById('helpQ2')) document.getElementById('helpQ2').textContent = lang.helpQ2;
        if (document.getElementById('helpA2')) document.getElementById('helpA2').textContent = lang.helpA2;
        if (document.getElementById('helpQ3')) document.getElementById('helpQ3').textContent = lang.helpQ3;
        if (document.getElementById('helpA3')) document.getElementById('helpA3').textContent = lang.helpA3;
        if (document.getElementById('helpAlgoTitle')) document.getElementById('helpAlgoTitle').textContent = lang.helpAlgo;
        if (document.getElementById('helpHuffman')) document.getElementById('helpHuffman').textContent = lang.helpHuffman;
        if (document.getElementById('helpLZW')) document.getElementById('helpLZW').textContent = lang.helpLZW;
        if (document.getElementById('helpMore')) document.getElementById('helpMore').textContent = lang.helpMore;
        if (fileNameDisplay && (!fileInput || !fileInput.files || fileInput.files.length === 0)) {
          fileNameDisplay.textContent = lang.noFileSelected;
        }
        if (document.getElementById('dropZoneTip')) {
          document.getElementById('dropZoneTip').textContent = lang.dropTip;
        }
        if (document.getElementById('resultTitle')) document.getElementById('resultTitle').textContent = lang.resultTitle;
        if (customFileBtn) customFileBtn.textContent = lang.selectFileBtn || '选择文件';
        if (customFileName && (!fileInput || !fileInput.files || fileInput.files.length === 0)) {
            customFileName.textContent = lang.noFileSelected;
            customFileName.classList.add('empty');
        }
    }

    if (customFileBtn && fileInput) {
        customFileBtn.onclick = () => fileInput.click();
    }
    if (fileInput && customFileName) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files.length > 0) {
                customFileName.textContent = `${i18n[currentLang].selectedFilePrefix} ${fileInput.files[0].name}`;
                customFileName.classList.remove('empty');
            } else {
                customFileName.textContent = i18n[currentLang].noFileSelected;
                customFileName.classList.add('empty');
            }
        });
    }

}); // 结束 DOMContentLoaded