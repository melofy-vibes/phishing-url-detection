document.addEventListener('DOMContentLoaded', async () => {
  const urlDisplay = document.getElementById('urlDisplay');
  const checkBtn = document.getElementById('checkBtn');
  const loading = document.getElementById('loading');
  const resultBox = document.getElementById('resultBox');

  // گرفتن URL تب فعال در مرورگر کروم
  let activeTabUrl = "";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
      activeTabUrl = tab.url;
      urlDisplay.textContent = activeTabUrl;
    } else {
      urlDisplay.textContent = "امکان دریافت آدرس این صفحه وجود ندارد.";
      checkBtn.disabled = true;
    }
  } catch (err) {
    urlDisplay.textContent = "خطا در خواندن آدرس تب جاری.";
  }

  // رویداد کلیک دکمه بررسی
  checkBtn.addEventListener('click', async () => {
    if (!activeTabUrl) return;

    // نمایش وضعیت لودینگ و مخفی کردن نتایج قبلی
    loading.style.display = 'block';
    resultBox.style.display = 'none';
    resultBox.className = 'result';

    try {
      // ارسال درخواست به سرور محلی پایتون
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: activeTabUrl })
      });

      if (!response.ok) {
        throw new Error('خطا در پاسخ‌دهی سرور API');
      }

      const data = await response.json();
      
      // تحلیل پاسخ سرور و نمایش در UI
      loading.style.display = 'none';
      resultBox.style.display = 'block';

      if (data.prediction === 1) {
        resultBox.classList.add('malicious');
        resultBox.innerHTML = `⚠️ لینک مخرب شناسایی شد!<br>احتمال تخریب: ${(data.probability * 100).toFixed(1)}%`;
      } else {
        resultBox.classList.add('safe');
        resultBox.innerHTML = `✅ لینک ایمن به نظر می‌رسد.<br>احتمال تخریب: ${(data.probability * 100).toFixed(1)}%`;
      }

    } catch (error) {
      loading.style.display = 'none';
      resultBox.style.display = 'block';
      resultBox.classList.add('malicious');
      resultBox.textContent = 'خطا در ارتباط با سرور هوش مصنوعی. مطمئن شوید سرور پایتون در حال اجرا است.';
      console.error(error);
    }
  });
});
