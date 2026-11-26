# مصنع ريلز صوتي — Stack E (عربي)

> انسخ الكتلة التالية إلى Claude Code داخل هذا الريبو. اللغة الافتراضية `ar`، والاتجاه RTL إلزامي. لا مفاتيح API، لا رصيد، ولا نشر.

```text
أريد ريلزاً عمودياً 1080×1920 / 30 إطاراً من ملف صوت عربي، بكابشن كلمة-بكلمة وحركة مضبوطة على كل إطار، باستخدام الـ harness الموجود في هذا الريبو فقط.

اعمل كالتالي، وتوقف بعد كل مرحلة لعرض الملفات الناتجة وطلب موافقتي:

0) افحص البيئة بـ npm run doctor، ثم اقرأ reel-state.json واستأنف من آخر stage. ثبّت الإصدارات من package.json وrequirements.txt؛ لا ثبّت شيئاً جديداً ولا تنزل نموذجاً قبل موافقتي. لا مفاتيح API ولا HF token ولا diarization لمتحدث واحد.

1) نظّف الصوت أولاً: npm run clean -- --project videos/ar-reel --input <ملف الصوت>. الناتج audio/clean.wav وaudio/edits.json. كل التوقيتات بعدها على الصوت النظيف؛ أي قص لاحق يستلزم إعادة حساب البدايات والنهايات من edits.json.

2) وقت الكلمات: إن كانت النماذج مخزنة في models/ فاستخدم npm run align -- --lang ar --project videos/ar-reel --align-backend whisperx مع --language ar و align_model="jonatasgrosman/wav2vec2-large-xlsr-53-arabic" صراحة. احتفظ بالتشكيل في display وجرّده في align. أي رقم أو اسم لاتيني أو كلمة خارج قاموس النموذج: score:0 + interpolate nearest + ذكرها في QA. إن كان Hugging Face محجوباً استخدم --offline أو --from-json config/words.ar.example.json. الموديل لا يصحّح النص المعتمد، خصوصاً تلاوة القرآن والأرقام والأسماء.

3) المشاهد: اقرأ config/copy.ar.json وconfig/brand.json وconfig/facts.json. لا تخترع رقماً ولا تاريخاً ولا اسماً؛ أي قيمة ناقصة تصير [placeholder] وتعرض عليّ. حدود المشاهد من words.json لا من التخمين. كل الأصول محلية في assets/.

4) الحركة: npm run compose ثم npm run render. تايم لاين GSAP واحد paused وseeked إلى زمن الفيلم؛ ممنوع الساعات المستقلة، العشوائية غير المثبتة، requestAnimationFrame، والأصول الشبكية. HyperFrames هو المسار عالي الجودة، وPillow بديل بلا Chrome فقط. لا تجمع HyperFrames مع Remotion في نفس المشروع.

5) الكابشن RTL: <div dir="rtl" lang="ar" style="direction:rtl;unicode-bidi:isolate">، سطر عربي كامل مشكّل، وكلمة نشطة يُغيّر لونها داخل السطر فقط. الأرقام والأسماء اللاتينية داخل <bdi>. خط Scheherazade New أو Amiri مع ملف OFL. أول كابشن خلال 1.5 ثانية، والفيديو مفهوم بلا صوت. النطاق الآمن للمنصات: y 288–1248 وx 120–888، وتضيق الجهة اليمنى إلى 780 تحت y 840؛ الكابشن عند أسفل النطاق.

6) التصدير والجودة: المحرك يدمج الصوت مرة واحدة؛ FFmpeg بعده للفحص والجهارة ≈ −14 LUFS ولقطات المراجعة فقط، لا دمج ثانٍ. شغّل npm run qa، وافتح qa/contact-sheet.jpg وqa/report.md. تحقق من المدة، الدقة، الإطارات، وجود مسار صوت واحد، اتجاه الهايلايت يمين→يسار، الكلمات غير المؤكدة، وعدم وجود أرقام مختلقة. أي فشل حرج: لقطة ← اقرأ ← أصلح ← أعد التصدير، محاولتان كحد أقصى ثم اسألني.

7) حدّث reel-state.json بعد كل مرحلة، واكتب تكلفة صفرية: api_calls=[] وcredits_spent=0. الناتج draft فقط: out/reel-ar.mp4 + captions.srt + qa/report.md. لا تنشر ولا ترفع ولا تشترِ رصيداً ولا تعدّل مشاريع videos/ المرجعية إلا بأمر صريح.

استخدم npm run reel -- --lang ar --project videos/ar-reel --input <ملف الصوت> لتشغيل السلسلة، أو --demo --offline لتجربة حتمية بلا نماذج.
```

المرجع المطوّل للتصحيحات الثمانية وجدول الأدوات الـ12: `research/stack-blueprint/audio-first-arabic/PROMPT.ar.md`.
