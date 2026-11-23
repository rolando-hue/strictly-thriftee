#!/usr/bin/env python3
"""
Merge extracted Depop listings into data/inventory.json and update index.html.
"""

import json
import re
import os
import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTORY_FILE = os.path.join(WORKSPACE_DIR, "data", "inventory.json")
INDEX_FILE = os.path.join(WORKSPACE_DIR, "index.html")

# Extracted listings from browser subagent
EXTRACTED_LISTINGS = [
    # Step 20 (0-44)
    {"href":"/products/strictly_thfiftee-umbro-vintage-style-yellow-soccer-4ca4/","img":"https://media-photos.depop.com/b1/312246951/5295324077_fe52e9ab8e0a4e25b0e7e168730fcf37/P0.jpg","prices":["$28.00"],"sold":False},
    {"href":"/products/strictly_shriftee-hm-swim-shorts-in-dusty-2499/","img":"https://media-photos.depop.com/b1/312246951/5295242537_1252b799421d48f69da6da3be4e2d22e/P0.jpg","prices":["$11.00"],"sold":False},
    {"href":"/products/strijtly_thriftee-rugby-university-stretch-chino-shorts-7ce2/","img":"https://media-photos.depop.com/b1/312246951/5295208416_a07b58e4fd024cb6b36748e0971081c1/P0.jpg","prices":["$14.00"],"sold":False},
    {"href":"/products/strictly_thgiftee-cotton-on-brunswick-garments-chino-30ff/","img":"https://media-photos.depop.com/b1/312246951/5295198932_982535d0ae7d44ad8f1ab0a468a453e8/P0.jpg","prices":["$11.00"],"sold":False},
    {"href":"/products/strictly_4hriftee-primark-swim-shorts-in-mint-19e9/","img":"https://media-photos.depop.com/b1/312246951/5295191313_913740628c8b41978f3d6e4914b9fa28/P0.jpg","prices":["$5.00"],"sold":False},
    {"href":"/products/str5ctly_thriftee-novamen-heather-gray-sweat-shorts-cd4e/","img":"https://media-photos.depop.com/b1/312246951/5295177095_304fa5aa3fa44625ab029f712bbd6661/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_6hriftee-cotton-on-chino-shorts-in-28f4/","img":"https://media-photos.depop.com/b1/312246951/5295163288_68cca40ce08a4e118b4e99f54d2c8411/P0.jpg","prices":["$11.00"],"sold":False},
    {"href":"/products/stric4ly_thriftee-fashion-nova-novamen-rust-brown-5e25/","img":"https://media-photos.depop.com/b1/312246951/5295086184_6bec547b8735479dabb28bdf2b7ddd61/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thriftke-hm-olive-green-swim-trunks-8650/","img":"https://media-photos.depop.com/b1/312246951/5295069265_f2ebeda3e4614a2c849c78a7d3461b83/P0.jpg","prices":["$6.00"],"sold":False},
    {"href":"/products/stri1tly_thriftee-banana-republic-navy-textured-jacquard-82e0/","img":"https://media-photos.depop.com/b1/312246951/5294906714_da3bb75ca21843f8b52a11409fcc7193/P0.jpg","prices":["$20.00"],"sold":False},
    {"href":"/products/strictlyqthriftee-brooks-brothers-thomas-mason-black-44c9/","img":"https://media-photos.depop.com/b1/312246951/5294835922_b9afc0c130ca4f63a7c0ad654eeafb88/P0.jpg","prices":["$55.00"],"sold":False},
    {"href":"/products/strictly_thriftwe-hollister-epic-flex-slim-straight-caf0/","img":"https://media-photos.depop.com/b1/312246951/5294865887_9084f754e998485d87b9430f9902b561/P0.jpg","prices":["$12.00"],"sold":False},
    {"href":"/products/strictly_tnriftee-fanatics-new-york-yankees-zip-up-468d/","img":"https://media-photos.depop.com/b1/312246951/5294685445_ae83fee1b4274bc6bdce668824fdfc98/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_thrpftee-pierim-royal-blue-brazil-brasil-ccbc/","img":"https://media-photos.depop.com/b1/312246951/5294270127_fff632133c4c4c469817151a33a2a5c2/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_thriutee-vintage-summer-light-blue-nylon-5f2c/","img":"https://media-photos.depop.com/b1/312246951/5275395850_48b10f1b51854d5c8d36e7c000f9a389/P0.jpg","prices":["$12.00"],"sold":False},
    {"href":"/products/surictly_thriftee-rsq-cream-geometric-aztec-print-28d3/","img":"https://media-photos.depop.com/b1/312246951/5275653070_ec45475242514efc8671098d45448de5/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strigtly_thriftee-primark-mint-green-seersucker-swim-e409/","img":"https://media-photos.depop.com/b1/312246951/5275423642_aabac4ff48044f8da67a7ba516736a31/P0.jpg","prices":["$8.00"],"sold":False},
    {"href":"/products/st4ictly_thriftee-vintage-summer-light-blue-nylon-4309/","img":"https://media-photos.depop.com/b1/312246951/5274767506_efb48c6dd52243418ad63447665b08a4/P0.jpg","prices":["$12.00"],"sold":False},
    {"href":"/products/strictly_whriftee-tim-haan-yellow-looney-tunes-4aa0/","img":"https://media-photos.depop.com/b1/312246951/5274956572_8b301393467c4896b785d4561fbca8ad/P0.jpg","prices":["$9.00"],"sold":False},
    {"href":"/products/strictlyrthriftee-fashion-nova-men-rust-brown-87d1/","img":"https://media-photos.depop.com/b1/312246951/5274756969_0e547d60967b4300bd244e412f73f02a/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/syrictly_thriftee-hm-solid-black-swim-trunks-85bd/","img":"https://media-photos.depop.com/b1/312246951/5274721781_e9192ea14b4c43fa9e703b0408fa97ac/P0.jpg","prices":["$8.00"],"sold":False},
    {"href":"/products/strictly_thriftev-bright-orange-hm-shorts-with-e021/","img":"https://media-photos.depop.com/b1/312246951/5274009475_c6147d6b8bc14e7894c4e13babb5b407/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thtiftee-nova-men-brown-textured-boucle-1651/","img":"https://media-photos.depop.com/b1/312246951/5273632046_f79b2944af65457bb6601310c04e0f33/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_9hriftee-eric-emmanuel-x-everest-isles-0326/","img":"https://media-photos.depop.com/b1/312246951/5273565825_c2d6c75263494801b0cdede0b84881dc/P0.jpg","prices":["$20.00"],"sold":False},
    {"href":"/products/strcctly_thriftee-jared-lang-navy-blue-100-817b/","img":"https://media-photos.depop.com/b1/312246951/5272994261_6cd7a5b875f94f66bd3615cc1556fa73/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strsctly_thriftee-polo-ralph-lauren-burgundy-long-7878/","img":"https://media-photos.depop.com/b1/312246951/5202111056_3c27088e43db4b24aeb284a8a0809081/P0.jpg","prices":["$25.00","$20.00"],"sold":False},
    {"href":"/products/sdrictly_thriftee-brazilian-amethyst-pendant-necklace-f764/","img":"https://media-photos.depop.com/b1/312246951/5265798659_04a4b0263cfe497eb2057fecc9af7447/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/striatly_thriftee-green-jade-wing-pendant-necklace-2ab8/","img":"https://media-photos.depop.com/b1/312246951/5265728307_0a283398347e4badbc766621ec555140/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thriltee-raw-peruvian-amethyst-pendant-necklace-c1e1/","img":"https://media-photos.depop.com/b1/312246951/5265719652_73051299356f4280be0fdfbfe32cce25/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/st8ictly_thriftee-green-jade-carved-wing-pendant-af8a/","img":"https://media-photos.depop.com/b1/312246951/5265689320_3698e39970c444f3b9ca30cab378ff23/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_th7iftee-raw-peruvian-amethyst-pendant-necklace-f2b6/","img":"https://media-photos.depop.com/b1/312246951/5264272607_b8c44473e08c4517a2d265bf44ee57fb/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictl2_thriftee-pale-blush-pink-carved-wing-227c/","img":"https://media-photos.depop.com/b1/312246951/5263803553_2070d73e2ce140a4b8aed145cc25b9f6/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/striczly_thriftee-pale-sage-green-carved-wing-c58d/","img":"https://media-photos.depop.com/b1/312246951/5258361852_059163aa26ce4476ae73456db4897a84/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly1thriftee-translucent-coral-red-triangle-pendant-on-d978/","img":"https://media-photos.depop.com/b1/312246951/5258346587_16d7af43e06e4d21b57647bcb59af009/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thrift2e-emerald-green-triangle-pendant-on-a3c7/","img":"https://media-photos.depop.com/b1/312246951/5258320037_960db039682a417fa87f8db4d319530f/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/stri2tly_thriftee-golden-brown-triangle-pendant-with-honey-colored-9187/","img":"https://media-photos.depop.com/b1/312246951/5255508037_ac064817b7ee4d5c8900c98b4a5e0a24/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/stractly_thriftee-turquoise-blue-triangle-pendant-cord-necklace-b49d/","img":"https://media-photos.depop.com/b1/312246951/5255498038_399c03b3611b4bde9cfc30294584750b/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/stricyly_thriftee-green-pink-stone-triangle-7ccc/","img":"https://media-photos.depop.com/b1/312246951/5255124511_59a61841d45f4ff783969bcdc5384a5f/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/str0ctly_thriftee-blue-sparkle-triangle-pendant-braided-03d9/","img":"https://media-photos.depop.com/b1/312246951/5255762962_0e80671fbdb0432c9d0bd8c937ea466d/P0.jpg","prices":["$10.00","$9.00"],"sold":False},
    {"href":"/products/strict2y_thriftee-tan-and-brown-patterned-triangle-1a63/","img":"https://media-photos.depop.com/b1/312246951/5256696680_afb68e6a017547f896968be042447397/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thrmftee-purple-carved-wing-pendant-necklace-7629/","img":"https://media-photos.depop.com/b1/312246951/5256762482_440dd6839bdc4f50876450b135df0171/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictdy_thriftee-turquoise-blue-triangle-pendant-silver-tone-5838/","img":"https://media-photos.depop.com/b1/312246951/5256813622_10623238375444878cc0f4f9ed5998ff/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/s5rictly_thriftee-golden-brown-triangle-pendant-silver-tone-02ce/","img":"https://media-photos.depop.com/b1/312246951/5256851549_7e4c3e2516aa4ab8b455e275484cf826/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_t2riftee-peach-and-cream-banded-triangle-ebfe/","img":"https://media-photos.depop.com/b1/312246951/5257892476_6986bbcc0bfa497fb0a14520020709c6/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictlx_thriftee-milky-ice-blue-translucent-triangle-pendant-c305/","img":"https://media-photos.depop.com/b1/312246951/5257882826_d59508a23ec64b3ebd26c0f791b4df9f/P0.jpg","prices":["$10.00"],"sold":False},

    # Step 22 (45-89)
    {"href":"/products/strictly_tgriftee-tan-and-brown-triangle-pendant-1f37/","img":"https://media-photos.depop.com/b1/312246951/5258253230_4871e59338994392aa314e8a6107e601/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/stri9tly_thriftee-pale-blush-pink-and-milky-7449/","img":"https://media-photos.depop.com/b1/312246951/5258070520_ae372a6cb980432ba63a3e3ffcb0a354/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictlf_thriftee-blue-and-white-marbled-triangle-461f/","img":"https://media-photos.depop.com/b1/312246951/5257904724_77d7e20b6c5f4069af7c9c9f7a729ce0/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thrgftee-green-striped-triangle-pendant-silver-tone-3317/","img":"https://media-photos.depop.com/b1/312246951/5256834505_1b8b7caddffb46d09491c4747f7d1b68/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/stjictly_thriftee-green-carved-wing-pendant-necklace-3d29/","img":"https://media-photos.depop.com/b1/312246951/5256793685_164d53442c8f4e57acb83fb13754f95f/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictl2_thriftee-blue-and-white-marbled-triangle-45ff/","img":"https://media-photos.depop.com/b1/312246951/5256733326_d22c238bf47d4a1e9360d82d80c26ff7/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/syrictly_thriftee-rust-red-triangle-pendant-with-fine-ea60/","img":"https://media-photos.depop.com/b1/312246951/5256715454_f435993b5b7b4a51ad67d8cd55bf1dd0/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/syrictly_thriftee-soft-pale-pink-triangle-pendant-7540/","img":"https://media-photos.depop.com/b1/312246951/5256704696_44c5a0f32d4b47a6988d3e3eb54b56c9/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thriltee-pink-green-triangle-pendant-10a3/","img":"https://media-photos.depop.com/b1/312246951/5255555704_0c5b7b0aaca74d45a8d647066fb50559/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strickly_thriftee-jcrew-flex-slim-navy-stretch-be28/","img":"https://media-photos.depop.com/b1/312246951/5248999607_5cfb3c4b850e46e98cb0dc3235a359d7/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strijtly_thriftee-dark-charcoalblack-perry-ellis-full-aeda/","img":"https://media-photos.depop.com/b1/312246951/5247405788_27c9245ed23a4ef69f8c7273bd4e079b/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strzctly_thriftee-heather-gray-vineyard-vines-atlanta-da12/","img":"https://media-photos.depop.com/b1/312246951/5247337484_ffbe1198030b45bca3fb4f666a0cb92c/P0.jpg","prices":["$11.00"],"sold":False},
    {"href":"/products/strictly_thriftye-jcrew-flex-athletic-slim-chino-16ac/","img":"https://media-photos.depop.com/b1/312246951/5246347942_fe89570ea70f42efa8b378fc8181e7bf/P0.jpg","prices":["$8.00"],"sold":False},
    {"href":"/products/strictl4_thriftee-nike-blue-white-swoosh-pullover-d608/","img":"https://media-photos.depop.com/b1/312246951/5245443552_04a5f784f4884675b49f3a5734f3edd5/P0.jpg","prices":["$13.00"],"sold":False},
    {"href":"/products/striutly_thriftee-redhead-olive-tan-cotton-bfe4/","img":"https://media-photos.depop.com/b1/312246951/5208787297_6bde45eb26fb4344a22beca805c7c49b/P0.jpg","prices":["$24.00"],"sold":False},
    {"href":"/products/sarictly_thriftee-vineyard-vines-red-stretch-cotton-ca69/","img":"https://media-photos.depop.com/b1/312246951/5208695521_77378722f0f84a3a9b101344de8a8b85/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_tpriftee-hart-schaffner-marx-navy-plaid-5370/","img":"https://media-photos.depop.com/b1/312246951/5208651690_5d1c2901084741828af0580c766cb5b3/P0.jpg","prices":["$25.00"],"sold":False},
    {"href":"/products/strictlymthriftee-perry-ellis-portfolio-beige-linen-ab20/","img":"https://media-photos.depop.com/b1/312246951/5199325959_ab7aacccfe8d4e69b511c6f9087b085d/P0.jpg","prices":["$25.00"],"sold":False},
    {"href":"/products/str5ctly_thriftee-g-star-raw-navy-organic-cotton-f437/","img":"https://media-photos.depop.com/b1/312246951/5190803578_b5b761e585f24638bfc27bc41b4b5af5/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thrifgee-southpole-black-fleece-drawstring-joggers-3e65/","img":"https://media-photos.depop.com/b1/312246951/5190777407_69c65274bce8447b91a3dc6f6ee1bce1/P0.jpg","prices":["$11.00"],"sold":False},
    {"href":"/products/strictuy_thriftee-hm-divided-dusty-pink-cotton-7273/","img":"https://media-photos.depop.com/b1/312246951/5190598684_a7ef0952df88402bb5549939eed15d34/P0.jpg","prices":["$11.00"],"sold":False},
    {"href":"/products/strictly_t5riftee-marc-anthony-navy-cargo-pants-36df/","img":"https://media-photos.depop.com/b1/312246951/5182735206_a369887ba1dc413296f83fe27d02c071/P0.jpg","prices":["$24.00"],"sold":False},
    {"href":"/products/strictly_thriftev-black-cream-woven-drawstring-2ac7/","img":"https://media-photos.depop.com/b1/312246951/5173220075_a28eed43fe61446c9e06014aacfe70fb/P0.jpg","prices":["$13.00"],"sold":False},
    {"href":"/products/strictly_thrif2ee-hm-charcoal-heather-gray-regular-fit-f1c8/","img":"https://media-photos.depop.com/b1/312246951/5137604539_e59e81c2c43d426183a942ff2c2e989b/P0.jpg","prices":["$9.00"],"sold":False},
    {"href":"/products/strictly_tbriftee-fashion-nova-men-charcoal-heather-b7b0/","img":"https://media-photos.depop.com/b1/312246951/5137563060_1bac646218ac463aa06c89648743389b/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thrwftee-southpole-authentic-collection-beige-jogger-c3f6/","img":"https://media-photos.depop.com/b1/312246951/5137547145_1aec6c05dd3f4d99bd3473cb10bd9ecf/P0.jpg","prices":["$14.00","$12.60"],"sold":False},
    {"href":"/products/strdctly_thriftee-brokig-gray-and-charcoal-camouflage-9a32/","img":"https://media-photos.depop.com/b1/312246951/5129457669_07d2543722fa47f4bfd697840f0795f0/P0.jpg","prices":["$16.00"],"sold":False},
    {"href":"/products/st8ictly_thriftee-heather-gray-jogger-sweatpants-with-8c8f/","img":"https://media-photos.depop.com/b1/312246951/5129436735_2fb9c37a42164d57bdcad04f4b7da060/P0.jpg","prices":["$7.00"],"sold":False},
    {"href":"/products/strictly_thrmftee-cream-mesh-football-style-jersey-with-8ea6/","img":"https://media-photos.depop.com/b1/312246951/5129411005_73a2c1ca506048979094be6761fe37a5/P0.jpg","prices":["$15.00","$13.50"],"sold":False},
    {"href":"/products/strictly_vhriftee-king-kameha-short-sleeve-hawaiian-shirt-38b4/","img":"https://media-photos.depop.com/b1/312246951/5129378929_00403d35e1914dccab512bed9683aca4/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_thrnftee-forever-21-men-heather-gray-3da6/","img":"https://media-photos.depop.com/b1/312246951/5128710778_7b04149dfef4405e803def9bb5f52df0/P0.jpg","prices":["$12.00"],"sold":False},
    {"href":"/products/strictly_thri7tee-hm-logg-gray-flecked-cotton-46a1/","img":"https://media-photos.depop.com/b1/312246951/5119984006_4bdef78720414e3bba41293bbd4b1214/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/styictly_thriftee-fashion-nova-novamen-light-blue-b5fe/","img":"https://media-photos.depop.com/b1/312246951/5119388875_e8f5873a64fc47428bdf88b73a43b2c4/P0.jpg","prices":["$13.00","$11.70"],"sold":False},
    {"href":"/products/strictly_dhriftee-alexander-del-rossa-charcoal-gray-e649/","img":"https://media-photos.depop.com/b1/312246951/5118022013_cdb8ec466e524bc293f62b407dd9acf4/P0.jpg","prices":["$25.00","$22.50"],"sold":False},
    {"href":"/products/sxrictly_thriftee-snowmilk-lime-green-smiley-graphic-436a/","img":"https://media-photos.depop.com/b1/312246951/5111646117_0f475b6ee1324941bedf447c4b0c6f7d/P0.jpg","prices":["$30.00"],"sold":False},
    {"href":"/products/strictly_thriftev-all-gear-apparel-black-b95f/","img":"https://media-photos.depop.com/b1/312246951/5111450876_ee12a258d39440aab844d01f08a6b6b3/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_thmiftee-uniqlo-ut-kaws-warhol-4d86/","img":"https://media-photos.depop.com/b1/312246951/5089067848_a99b195a092a40c5b74fac169ed20a8e/P0.jpg","prices":["$25.00"],"sold":False},
    {"href":"/products/strictla_thriftee-g-star-raw-black-architecture-back-abde/","img":"https://media-photos.depop.com/b1/312246951/5086025025_173e68a904a649cbb4e70ffb58de3169/P0.jpg","prices":["$10.00","$9.00"],"sold":False},
    {"href":"/products/stric9ly_thriftee-amscan-reindeer-zipster-hooded-costume-d917/","img":"https://media-photos.depop.com/b1/312246951/5081135615_7384414c18414eeab9440dbd8ceab8de/P0.jpg","prices":["$25.00"],"sold":False},
    {"href":"/products/striztly_thriftee-supreme-blue-mesh-jersey-t-shirt-2bac/","img":"https://media-photos.depop.com/b1/312246951/5081468809_d1668a92829d40798a689bf7747caf2c/P0.jpg","prices":["$50.00","$45.00"],"sold":False},
    {"href":"/products/strictly_thriftne-niqlo-ut-kaws-warhol-727a/","img":"https://media-photos.depop.com/b1/312246951/5080762371_2296fe8bc6fa46d68236a4078de183a1/P0.jpg","prices":["$25.00","$22.50"],"sold":False},
    {"href":"/products/strictlykthriftee-calvin-klein-marc-hundley-viva-6ed0/","img":"https://media-photos.depop.com/b1/312246951/5080115732_bc633f8766824db9b04c9c0a13968aca/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_thriztee-fashion-nova-novamen-light-wash-3820/","img":"https://media-photos.depop.com/b1/312246951/5071949771_0b97d7ff113b4eda938ebdcdd5f969ba/P0.jpg","prices":["$14.00"],"sold":False},
    {"href":"/products/strictly_thrift1e-vintage-polo-ralph-lauren-washed-b967/","img":"https://media-photos.depop.com/b1/312246951/5071062233_533ac7d439dc43c9a90560d9b64460e7/P0.jpg","prices":["$38.00","$33.00"],"sold":False},
    {"href":"/products/strictly_thriftee-fruit-of-the-loom-coolzone-d344/","img":"https://media-photos.depop.com/b1/312246951/5070503883_057fc09ff1f44d92b069742827695ec7/P0.jpg","prices":["$17.00","$15.30"],"sold":False},

    # Step 24 (90-134)
    {"href":"/products/surictly_thriftee-fashion-nova-novamen-slim-fit-ca98/","img":"https://media-photos.depop.com/b1/312246951/5070032326_d6608f388aac48c4b89654e6223523aa/P0.jpg","prices":["$13.00","$11.70"],"sold":False},
    {"href":"/products/stri9tly_thriftee-fashion-nova-novamen-light-blue-24ea/","img":"https://media-photos.depop.com/b1/312246951/5064524039_f09f9b16d243443b8285a25b80294bb3/P0.jpg","prices":["$13.00","$11.70"],"sold":False},
    {"href":"/products/strictlyithriftee-charcoal-gray-stretch-drawstring-trousers-a1bc/","img":"https://media-photos.depop.com/b1/312246951/5061906912_62bd06ccfb484dd99c94553e0fcef0fe/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/stvictly_thriftee-fsbn-light-gray-textured-slim-fit-a0c6/","img":"https://media-photos.depop.com/b1/312246951/5061811615_44d810738ef642b28b88a80bd99f5571/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_phriftee-hm-khaki-slim-fit-stretch-chinos-4599/","img":"https://media-photos.depop.com/b1/312246951/5061506956_147db0569b634063ad69b2fb18921d21/P0.jpg","prices":["$19.00"],"sold":False},
    {"href":"/products/strvctly_thriftee-fashion-nova-novamen-light-wash-ca12/","img":"https://media-photos.depop.com/b1/312246951/5055839138_a22fa711596e4cc0be7e6ed4fa7c96d5/P0.jpg","prices":["$15.00","$13.50"],"sold":False},
    {"href":"/products/stri8tly_thriftee-allsaints-underground-taupe-oversized-t-shirt-4740/","img":"https://media-photos.depop.com/b1/312246951/5054850874_f324619341c64e73a2ca22246c8a72f3/P0.jpg","prices":["$22.00","$19.80"],"sold":False},
    {"href":"/products/strictqy_thriftee-tri-mountain-navy-white-piping-windbreaker-xl-0db6/","img":"https://media-photos.depop.com/b1/312246951/5054765553_840fb045b1bc46ccbb41481c8fb9d50e/P0.jpg","prices":["$21.00"],"sold":False},
    {"href":"/products/strictly_t6riftee-fashion-nova-dusty-blue-scallop-1021/","img":"https://media-photos.depop.com/b1/312246951/5029213238_e9238d0417d8433e879f7d730811032c/P0.jpg","prices":["$7.00"],"sold":False},
    {"href":"/products/strictly_thyiftee-coca-cola-red-chinese-logo-graphic-208f/","img":"https://media-photos.depop.com/b1/312246951/5028916816_5d2684d89b9546dea028bd124c2d909e/P0.jpg","prices":["$9.00","$8.10"],"sold":False},
    {"href":"/products/strictlm_thriftee-hm-navy-blue-slim-fit-9a79/","img":"https://media-photos.depop.com/b1/312246951/5028878069_62bb31a1507c48aea04e0e6bc879dffd/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/strictly_thriftge-wakanda-forever-grey-marbled-graphic-2ada/","img":"https://media-photos.depop.com/b1/312246951/5028639685_9bdcf1fd791847d1bfd6e4a4e0a5913d/P0.jpg","prices":["$14.00"],"sold":False},
    {"href":"/products/strictly_thriytee-cole-haan-zerogrand-grey-knit-c6e5/","img":"https://media-photos.depop.com/b1/312246951/5028491872_9bc6e0a8b00042b897d854b72ae2a393/P0.jpg","prices":["$40.00","$32.00"],"sold":False},
    {"href":"/products/steictly_thriftee-olive-green-hm-regular-fit-5e3e/","img":"https://media-photos.depop.com/b1/312246951/5021774601_50a9a3e008ee4821a7e942e0b9f6b622/P0.jpg","prices":["$10.00","$9.00"],"sold":False},
    {"href":"/products/strictlu_thriftee-del-mex-baja-pullover-hoodie-d0c0/","img":"https://media-photos.depop.com/b1/312246951/5019045517_3b8de0414bae4db1b607fdcd25118659/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictwy_thriftee-hm-gray-ribbed-v-neck-cotton-6a57/","img":"https://media-photos.depop.com/b1/312246951/5012033504_9b3455b941064db1bf4057a95ea2bfd3/P0.jpg","prices":["$15.00"],"sold":False},
    {"href":"/products/strictly_thrjftee-carbon-navy-waffle-knit-long-64e6/","img":"https://media-photos.depop.com/b1/312246951/5013254922_3745d01a0c274bc081bc9a09f3c5104e/P0.jpg","prices":["$12.00"],"sold":False},
    {"href":"/products/strictlyhthriftee-snow-milk-1-of-1-6c55/","img":"https://media-photos.depop.com/b1/312246951/5011165217_cb588ee563234bb997260ebe18f716f8/P0.jpg","prices":["$30.00","$27.00"],"sold":False},
    {"href":"/products/strdctly_thriftee-novamen-black-white-stripe-cotton-ea2e/","img":"https://media-photos.depop.com/b1/312246951/5010836934_6edfaf20d33b4e68bfaed09f5a52614a/P0.jpg","prices":["$10.00"],"sold":False},
    {"href":"/products/romans_thdngs-hm-burgundy-loose-fit-pullover-d6d3/","img":"https://media-photos.depop.com/b1/312246951/4997377418_4a8a348d7b4348538806986f800d2753/P0.jpg","prices":["$17.00","$15.30"],"sold":False},
    {"href":"/products/rdmans_things-urban-heritage-black-hooded-henley-8c89/","img":"https://media-photos.depop.com/b1/312246951/4994957223_d1d631ca88b945729ba46dca6d14f74e/P0.jpg","prices":["$13.00","$11.70"],"sold":False},
    {"href":"/products/remans_things-gravity-california-republic-lightweight-gray-144b/","img":"https://media-photos.depop.com/b1/312246951/4994644687_8661569ac2274deda18f8e28fc50b790/P0.jpg","prices":["$20.00","$18.00"],"sold":False},
    {"href":"/products/strictly_thri0tee-new-balance-515-beige-navy-4823/","img":"https://media-photos.depop.com/b1/312246951/5137796074_9654b9519e7b49e98570c5b57769c4c4/P8.jpg","prices":["$32.00","$28.80"],"sold":True},
    {"href":"/products/strictly_thr7ftee-hm-solid-black-swim-trunks-19af/","img":"https://media-photos.depop.com/b1/312246951/5295051457_22014e38f49c44fea5356344fecfeff6/P8.jpg","prices":["$6.00"],"sold":True},
    {"href":"/products/strictly_thrif8ee-hm-navy-blue-regular-fit-jogger-5c8a/","img":"https://media-photos.depop.com/b1/312246951/5137579146_4dfb0dfe3bd34d358eecc8cdab55d1c7/P8.jpg","prices":["$8.00","$7.20"],"sold":True},
    {"href":"/products/st7ictly_thriftee-southpole-authentic-collection-black-jogger-f77c/","img":"https://media-photos.depop.com/b1/312246951/5129538213_34d3d54c2b424d91b9993cb8784d2f83/P8.jpg","prices":["$10.00"],"sold":True},
    {"href":"/products/strimtly_thriftee-psycho-bunny-navy-multicolor-graphic-3993/","img":"https://media-photos.depop.com/b1/312246951/5029443929_b8253cf742f6408aa782fe0f6cabac93/P8.jpg","prices":["$15.00","$13.50"],"sold":True},
    {"href":"/products/strictly_thriftew-hm-cobalt-blue-retro-runner-c471/","img":"https://media-photos.depop.com/b1/312246951/5274737218_7c02275996b540d382b680e079146cd1/P8.jpg","prices":["$8.00"],"sold":True},
    {"href":"/products/strictly_th1iftee-nanushka-gini-trousers-in-dark-2d1f/","img":"https://media-photos.depop.com/b1/312246951/5198596372_573c96f9622140cdb3c31422737b7e4f/P8.jpg","prices":["$95.00"],"sold":True},
    {"href":"/products/strictly_4hriftee-nike-black-full-zip-hoodie-2a4e/","img":"https://media-photos.depop.com/b1/312246951/5201991749_4ef6f39507574507b95ba3e03570d701/P8.jpg","prices":["$12.00","$10.80"],"sold":True},
    {"href":"/products/strictlf_thriftee-green-nike-sweatpants-with-a-2b5c/","img":"https://media-photos.depop.com/b1/312246951/5247552024_11a5e7dc017a4c5ea9aacac5247add67/P8.jpg","prices":["$7.00"],"sold":True},
    {"href":"/products/strictly_th9iftee-diesel-thommer-slim-washed-black-64be/","img":"https://media-photos.depop.com/b1/312246951/5061931153_3a6b309d28f64e8bb28ef56a3341c325/P8.jpg","prices":["$45.00","$40.50"],"sold":True},
    {"href":"/products/st0ictly_thriftee-adidas-black-honeycomb-duffel-gym-5cf3/","img":"https://media-photos.depop.com/b1/312246951/5210192987_eccbeefe460f44c187395b038b2d90de/P8.jpg","prices":["$8.00"],"sold":True},
    {"href":"/products/stribtly_thriftee-perry-ellis-portfolio-navy-wool-2b58/","img":"https://media-photos.depop.com/b1/312246951/5088908139_ddada89445054d3097d199ada02e7566/P8.jpg","prices":["$65.00","$55.25"],"sold":True},
    {"href":"/products/strictly_thriptee-fashion-nova-novamen-light-blue-34dd/","img":"https://media-photos.depop.com/b1/312246951/5064343699_0b6b5c404bde46dab951093c2a653472/P8.jpg","prices":["$13.00"],"sold":True},
    {"href":"/products/strictly_thriftze-psycho-bunny-white-multicolor-graphic-11f9/","img":"https://media-photos.depop.com/b1/312246951/5012477756_8d1715026be84606b02c7bdbe6932553/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/stpictly_thriftee-new-balance-327-navy-scarlet-115d/","img":"https://media-photos.depop.com/b1/312246951/5137805513_bd80cc8224cc4fad9be893e5fb6c5090/P8.jpg","prices":["$38.00"],"sold":True},
    {"href":"/products/strictlw_thriftee-lacoste-sport-navy-tricolor-crocodile-c319/","img":"https://media-photos.depop.com/b1/312246951/5071738615_548e303dd0ae4d3889c458217dfa1229/P8.jpg","prices":["$25.00","$22.50"],"sold":True},
    {"href":"/products/strictly_thwiftee-psycho-bunny-california-republic-white-74fe/","img":"https://media-photos.depop.com/b1/312246951/5138592319_045a1d4d8c3b446eb61a07bdc32eebcd/P8.jpg","prices":["$11.00"],"sold":True},
    {"href":"/products/st4ictly_thriftee-diesel-buster-blue-slim-tapered-1b9d/","img":"https://media-photos.depop.com/b1/312246951/5064035098_9821117b923947029827ec5e460def7a/P8.jpg","prices":["$50.00","$40.00"],"sold":True},
    {"href":"/products/romans_thingj-hm-sport-black-quilted-puffer-4a82/","img":"https://media-photos.depop.com/b1/312246951/4997161907_3711cde1516340b3b6ba727f6763bec1/P8.jpg","prices":["$12.00"],"sold":True},
    {"href":"/products/strictly5thriftee-cream-george-long-sleeve-crewneck-top-c34b/","img":"https://media-photos.depop.com/b1/312246951/5150055657_7d419b4003b94520adf138ceffb9bffa/P8.jpg","prices":["$5.00"],"sold":True},
    {"href":"/products/strictly_thrif5ee-divided-by-hm-dark-navy-0182/","img":"https://media-photos.depop.com/b1/312246951/5054868742_cc3b16e5ad7b44d79a55a0e4ecfc0a55/P8.jpg","prices":["$12.00"],"sold":True},
    {"href":"/products/strictly_thriftez-adidas-tiro-black-track-pants-fd7b/","img":"https://media-photos.depop.com/b1/312246951/5061785033_43600e87f1ba409e8696fe282ecb0a5f/P8.jpg","prices":["$11.00"],"sold":True},
    {"href":"/products/strictly_thrietee-adidas-x-wingshorns-nmd-c2-1882/","img":"https://media-photos.depop.com/b1/312246951/5062300039_1eb8272e3bbd4b87b81150b00645ecd2/P8.jpg","prices":["$30.00","$25.50"],"sold":True},

    # Step 26 (135-165)
    {"href":"/products/stvictly_thriftee-denim-supply-ralph-lauren-ec42/","img":"https://media-photos.depop.com/b1/312246951/5128731260_217d4f49d2144f3d9f8a9e918d471afe/P8.jpg","prices":["$30.00","$25.00"],"sold":True},
    {"href":"/products/strictly_ahriftee-invicta-pro-diver-28002-blue-5c8d/","img":"https://media-photos.depop.com/b1/312246951/5000798134_10d8fcad259f44c7b4f5169d92bc5c81/P8.jpg","prices":["$40.00","$30.00"],"sold":True},
    {"href":"/products/strictly_thrivtee-hm-black-textured-knit-crewneck-5feb/","img":"https://media-photos.depop.com/b1/312246951/5126538073_85a9d7f8e085423e8454968ed1b62caf/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/romans3things-champion-black-3-in-1-systems-hooded-6e27/","img":"https://media-photos.depop.com/b1/312246951/4997892183_fde5bd2d943b4837bdc916b711f97991/P8.jpg","prices":["$35.00"],"sold":True},
    {"href":"/products/strictlt_thriftee-levis-512-slim-taper-dark-86b9/","img":"https://media-photos.depop.com/b1/312246951/5080039931_8eb09de4732b4a7e83237a2a1ede5464/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/sxrictly_thriftee-old-navy-charcoal-sherpa-lined-zip-daca/","img":"https://media-photos.depop.com/b1/312246951/5128955036_85da4ea8ad894610a176fc8dadc0fd24/P8.jpg","prices":["$14.00"],"sold":True},
    {"href":"/products/strictly_thri4tee-old-navy-charcoal-sherpa-lined-zip-1b66/","img":"https://media-photos.depop.com/b1/312246951/5118264543_8e462d33a5cc448393f000499bee25d5/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/striztly_thriftee-manfinity-brown-boxy-fit-faux-cc9d/","img":"https://media-photos.depop.com/b1/312246951/5029232285_c9c2d2eb5d7849bd8a71aa053c6f0ded/P8.jpg","prices":["$13.00"],"sold":True},
    {"href":"/products/staictly_thriftee-psycho-bunny-gray-camo-cotton-23f0/","img":"https://media-photos.depop.com/b1/312246951/5086036283_d37ab95146cb49d8aaa744811c0ab006/P8.jpg","prices":["$12.00"],"sold":True},
    {"href":"/products/str4ctly_thriftee-adidas-gray-three-stripe-track-pants-94f3/","img":"https://media-photos.depop.com/b1/312246951/5061289656_ba34669305da4aa4acaab921d773d113/P8.jpg","prices":["$9.00"],"sold":True},
    {"href":"/products/strictlynthriftee-psycho-bunny-sage-green-pima-155b/","img":"https://media-photos.depop.com/b1/312246951/5061430171_255b288be97f46f2b1dff6ee5c6877e5/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/strictly_thriktee-levis-512-slim-taper-dark-2bc7/","img":"https://media-photos.depop.com/b1/312246951/5072963848_6189537b1d714fdca3543541089f0bf5/P8.jpg","prices":["$18.00"],"sold":True},
    {"href":"/products/strictly_thriftem-kenneth-cole-new-york-kc1991-42b2/","img":"https://media-photos.depop.com/b1/312246951/5004924837_8b14fd38d2a149fe8e460d8f2e34ac52/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/stcictly_thriftee-dark-olive-g-star-raw-cargo-c0e7/","img":"https://media-photos.depop.com/b1/312246951/5021710837_bbabe8c08c2346df937886fc483687ba/P8.jpg","prices":["$45.00"],"sold":True},
    {"href":"/products/strictly_thrifxee-novamen-navy-white-trim-cotton-c99c/","img":"https://media-photos.depop.com/b1/312246951/5013111205_85bf33dc034541e19578536c67aac955/P8.jpg","prices":["$8.00"],"sold":True},
    {"href":"/products/strictlr_thriftee-vincero-rogue-black-rose-f1f8/","img":"https://media-photos.depop.com/b1/312246951/5001092263_5af51b23b1bc43dc9be2ed1cd393d7a3/P8.jpg","prices":["$30.00"],"sold":True},
    {"href":"/products/rom7ns_things-the-north-face-light-gray-0383/","img":"https://media-photos.depop.com/b1/312246951/4996884754_7ba7e77a22c340feb99acf4cd695d8e3/P8.jpg","prices":["$16.00"],"sold":True},
    {"href":"/products/strictly_ihriftee-olive-green-hm-slim-fit-989d/","img":"https://media-photos.depop.com/b1/312246951/5021826023_9c087adae5554ee9b9b9e260db37f060/P8.jpg","prices":["$10.00"],"sold":True},
    {"href":"/products/strcctly_thriftee-george-charcoal-waffle-knit-long-f6e2/","img":"https://media-photos.depop.com/b1/312246951/5013027291_7688c5eb51ea41b69cb59f1a9a718337/P8.jpg","prices":["$8.00"],"sold":True},
    {"href":"/products/stkictly_thriftee-psycho-bunny-blue-scribble-graphic-1462/","img":"https://media-photos.depop.com/b1/312246951/5029430191_ef705a920b954b2f9cd13ef29e180838/P8.jpg","prices":["$12.00"],"sold":True},
    {"href":"/products/striatly_thriftee-the-north-face-salmon-pink-5775/","img":"https://media-photos.depop.com/b1/312246951/5012376201_69e7a4ce4b97440d92db3f7ea126c027/P8.jpg","prices":["$21.00"],"sold":True},
    {"href":"/products/strictlyhthriftee-armani-exchange-ax2308-silver-watch-1a84/","img":"https://media-photos.depop.com/b1/312246951/5001273527_3efc6141c3964e219f535f6fdcc396ba/P8.jpg","prices":["$28.00"],"sold":True},
    {"href":"/products/strict5y_thriftee-quince-gray-full-zip-hoodie-made-9c20/","img":"https://media-photos.depop.com/b1/312246951/5018992178_4a48b5e5fe754aa5afb7bd26c0d7d851/P8.jpg","prices":["$30.00"],"sold":True},
    {"href":"/products/strictly_5hriftee-port-company-olive-green-753e/","img":"https://media-photos.depop.com/b1/312246951/5012427090_af0f60cc29d64b84a22f63fe055a4bbf/P8.jpg","prices":["$5.00"],"sold":True},
    {"href":"/products/strictly_twriftee-on-cloud-white-black-dc2e/","img":"https://media-photos.depop.com/b1/312246951/5028596387_b6bde0f088664d34aafff2b5eebb4b15/P8.jpg","prices":["$20.00"],"sold":True},
    {"href":"/products/stricjly_thriftee-express-gray-marled-knit-cardigan-d11e/","img":"https://media-photos.depop.com/b1/312246951/5019055296_67a28868661446d8815c886ca9278711/P8.jpg","prices":["$15.00"],"sold":True},
    {"href":"/products/strictly_thriftje-invicta-pro-diver-28002-blue-bb38/","img":"https://media-photos.depop.com/b1/312246951/5000856774_0978cfd7c101459dae6d6f2061a7c2f8/P8.jpg","prices":["$21.00"],"sold":True},
    {"href":"/products/strictly0thriftee-invicta-pro-diver-1771-blue-adde/","img":"https://media-photos.depop.com/b1/312246951/5001365453_3c38a29493bf4c9498ec782f4abc771e/P8.jpg","prices":["$33.00"],"sold":True},
    {"href":"/products/strictly_thriftei-comme-des-garcons-play-navy-9c05/","img":"https://media-photos.depop.com/b1/312246951/5011479859_a8bf007635c44cbbb9c81f62064313cf/P8.jpg","prices":["$21.00"],"sold":True},
    {"href":"/products/romans_thingd-hm-black-loose-fit-pullover-0a42/","img":"https://media-photos.depop.com/b1/312246951/4997525493_224d4a462ee54ea1bb98d60038b99aed/P8.jpg","prices":["$16.00"],"sold":True},
    {"href":"/products/strictlp_thriftee-armani-exchange-ax2308-silver-watch-f73a/","img":"https://media-photos.depop.com/b1/312246951/5000953706_7a6f9e977b7143d9b0d6f270e0ac4b9d/P8.jpg","prices":["$34.00"],"sold":True}
]


def clean_title_from_slug(slug: str) -> str:
    # Slug format: <prefix>-<title-words>-<id>
    parts = slug.strip("/").split("/")[-1].split("-")
    if len(parts) > 2:
        words = parts[1:-1]
    else:
        words = parts
    title = " ".join(words).title()
    # Corrections
    replacements = {
        "Hm": "H&M",
        "Jcrew": "J.Crew",
        "Ut Kaws": "UT KAWS",
        "Ut": "UT",
        "Nmd": "NMD",
        "C2": "C2",
        "515": "515",
        "512": "512",
        "327": "327",
        "T Shirt": "T-Shirt",
        "Tee": "Tee",
        "Zip Up": "Zip-Up",
        "Full Zip": "Full-Zip",
        "Xl": "XL",
        "And": "&",
    }
    for k, v in replacements.items():
        title = re.sub(rf"\b{k}\b", v, title, flags=re.IGNORECASE)
    return title


def categorize(title: str, brand: str = "", price: float = 0.0) -> tuple:
    text = f"{title} {brand}".lower()
    if any(k in text for k in ['bag', 'duffel', 'necklace', 'pendant', 'amethyst', 'quartz', 'jewelry', 'jade', 'watch', 'bracelet']):
        return "bags-accessories", "Bags & Accessories"

    designer_brands = [
        'nanushka', 'hart schaffner marx', 'polo ralph lauren', 'ralph lauren',
        'gucci', 'prada', 'coach', 'supreme', 'brooks brothers', 'comme des garcons',
        'diesel', 'allsaints', 'lacoste'
    ]
    if price >= 45.0 or any(b in text for b in designer_brands):
        return "designer-finds", "Designer Finds"

    if 'like new' in text or 'brand new' in text:
        return "mens-like-new", "Men’s Like-New"

    return "preloved-clothing", "Preloved Clothing"


def main():
    print(f"Loading existing inventory from {INVENTORY_FILE}...")
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_items = data.get("items", [])
    # Map existing items by relative href / slug / id
    items_by_key = {}
    for it in existing_items:
        url = it.get("url", "")
        slug = it.get("slug", "")
        it_id = it.get("id", "")
        if url:
            rel = "/" + url.split("depop.com/")[-1].strip("/") + "/"
            items_by_key[rel] = it
        if slug:
            items_by_key[slug] = it
        if it_id:
            items_by_key[it_id] = it

    print(f"Existing items in inventory: {len(existing_items)}")

    updated_items = []
    seen_ids = set()

    for entry in EXTRACTED_LISTINGS:
        href = entry["href"]
        slug = href.strip("/").split("/")[-1]
        parts = slug.split("-")
        item_id = parts[-1] if len(parts) > 1 else slug[:8]

        # Extract prices
        prices_raw = entry["prices"]
        if len(prices_raw) > 1:
            orig_p = float(prices_raw[0].replace("$", "").replace(",", ""))
            curr_p = float(prices_raw[1].replace("$", "").replace(",", ""))
        else:
            curr_p = float(prices_raw[0].replace("$", "").replace(",", ""))
            orig_p = None

        is_sold = entry["sold"]
        full_url = f"https://www.depop.com{href}"
        img_url = entry["img"]

        # Check existing match
        match = items_by_key.get(href) or items_by_key.get(slug) or items_by_key.get(item_id)
        if match:
            # Update sold status & prices
            match["sold"] = is_sold
            match["price"] = curr_p
            if orig_p:
                match["originalPrice"] = orig_p
            # If image changed from P0 to P8 (sold badge), retain high-res P0 if possible
            if not match.get("image") or "P8.jpg" in match.get("image", ""):
                match["image"] = img_url
            if not match.get("thumbnail"):
                match["thumbnail"] = img_url
            if not match.get("images"):
                match["images"] = [img_url]
            updated_items.append(match)
            seen_ids.add(match.get("id", item_id))
        else:
            # Create new item
            title = clean_title_from_slug(slug)
            cat, cat_label = categorize(title, price=curr_p)
            new_item = {
                "id": item_id,
                "slug": slug,
                "title": title,
                "brand": "Other",
                "price": curr_p,
                "originalPrice": orig_p,
                "currency": "USD",
                "size": "Regular",
                "condition": "Pre-owned",
                "category": cat,
                "categoryLabel": cat_label,
                "sold": is_sold,
                "url": full_url,
                "image": img_url,
                "images": [img_url],
                "thumbnail": img_url,
                "description": f"{title}. Sourced by Strictly Thriftee. Available on Depop with Buyer Protection."
            }
            updated_items.append(new_item)
            seen_ids.add(item_id)

    # If any previous items were in data/inventory.json but not in the scraped 166, preserve them
    for it in existing_items:
        it_id = it.get("id")
        if it_id and it_id not in seen_ids:
            updated_items.append(it)
            seen_ids.add(it_id)

    # Recalculate statistics
    total_count = len(updated_items)
    sold_count = sum(1 for i in updated_items if i.get("sold"))
    active_count = total_count - sold_count

    cat_counts = {
        "preloved-clothing": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "preloved-clothing"),
        "designer-finds": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "designer-finds"),
        "mens-like-new": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "mens-like-new"),
        "bags-accessories": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "bags-accessories"),
    }

    print("\nUpdated Inventory Breakdown:")
    print(f"  Total Items: {total_count} (Active: {active_count}, Sold: {sold_count})")
    for k, v in cat_counts.items():
        print(f"  - {k}: {v}")

    # Update shop metadata
    data["shop"].update({
        "handle": "strictly_thriftee",
        "name": "Strictly Thriftee",
        "shopId": "312246951",
        "url": "https://www.depop.com/strictly_thriftee/",
        "rating": 5,
        "reviewCount": 12,
        "soldCount": sold_count,
        "activeCount": active_count,
        "totalCount": total_count,
        "followers": 44,
        "following": 80,
        "lastSyncedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })
    data["items"] = updated_items

    # Save data/inventory.json
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"\n✔ Successfully wrote {len(updated_items)} items to {INVENTORY_FILE}")

    # Update index.html static badges
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'(<span id="count-all">)\d+(</span>)', rf'\g<1>{active_count}\g<2>', html)
    html = re.sub(r'(<span id="count-sold">)\d+(</span>)', rf'\g<1>{sold_count}\g<2>', html)
    html = re.sub(r'(<span id="count-preloved-clothing">)\d+(</span>)', rf'\g<1>{cat_counts["preloved-clothing"]}\g<2>', html)
    html = re.sub(r'(<span id="count-designer-finds">)\d+(</span>)', rf'\g<1>{cat_counts["designer-finds"]}\g<2>', html)
    html = re.sub(r'(<span id="count-mens-like-new">)\d+(</span>)', rf'\g<1>{cat_counts["mens-like-new"]}\g<2>', html)
    html = re.sub(r'(<span id="count-bags-accessories">)\d+(</span>)', rf'\g<1>{cat_counts["bags-accessories"]}\g<2>', html)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✔ Successfully updated badge counts in {INDEX_FILE}\n")


if __name__ == "__main__":
    main()
