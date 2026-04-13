import json

def update_publications():
    with open('contents/structures/publications.json', 'r') as f:
        data = json.load(f)

    # Add status: published to existing items
    for section in data:
        for item in section['items']:
            item['status'] = 'published'

    new_items = [
        {
            "title": "Probabilistic Electricity Demand Forecasting for Buildings Using a VMD-Attentive Quantile Network",
            "journal": "Energy & Buildings",
            "authors": "Chun-Hao Huang, Yu-Shin Hu, I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Sector-specific Decarbonization Effects of High-Speed Rails Expansions",
            "journal": "Energy Economics",
            "authors": "Yoo, S., Kumagai, J., Hung-Jui Lin, Nakaishi, T., I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Digital Transformation and Carbon Redistribution in Warehouse Operations: Evidence from State-Persistent Simulation",
            "journal": "Operations Management Research",
            "authors": "Jian Hern Yeoh, Chun-Hao Huang, I-Yun Lisa Hsieh",
            "status": "submitted",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Advancing Circular Logistics: Life Cycle Assessment of Structurally Reinforced Modular Plastic Pallets",
            "journal": "Journal of Cleaner Production",
            "authors": "Cheng-Hsiang Shei, Ma, J. E., I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Adaptive and Multifaceted Vehicle-to-Building (V2B) Energy Management: A Two-Stage Framework Addressing User Expectations and Uncertainty",
            "journal": "eTransportation",
            "authors": "Yu-Shin Hu, I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Optimizing dynamic shared E-moped relocation with long-term effect via deep reinforcement learning",
            "journal": "Journal of Computing in Civil Engineering",
            "authors": "Jia-Cherng Song, I-Yun Lisa Hsieh, Chuin-Shan Chen",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Decarbonizing First-Mile Cold Chain Freight: Empirical Analysis of Heavy-Duty Refrigerated Truck Operations",
            "journal": "Journal of Cleaner Production",
            "authors": "Pei-Ci Chen, Hung-Jui Lin, Hsuan-Po Lin, I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Double Energy Vulnerability in Taiwan: Household Energy Poverty Across Domestic and Transport Domains",
            "journal": "Environmental Development",
            "authors": "Hsun-Yen Wu, Cheng-Hsiang Shei, John Chung-En Liu, I-Yun Lisa Hsieh",
            "status": "submitted",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Detection-Guided and Prompt-Augmented Transformers for Automated and Generalizable Cobb Angle Estimation in Spinal Radiographs",
            "journal": "IEEE Transactions on Medical Imaging",
            "authors": "Chih-Yi Lu, Tub, C. H., Hsieh, C. Y., Feng, C. K., I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Contrastive Representation Learning for Robust Cross-Site Very Short-Term Photovoltaic Forecasting",
            "journal": "IEEE Transactions on Industry Applications",
            "authors": "Chih-Yi Lu, I-Yun Lisa Hsieh",
            "status": "under-review",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Carbon pricing at the border: Product-level evidence on the impacts of the EU Carbon Border Adjustment Mechanism",
            "journal": "Climate Policy",
            "authors": "Shao-Yang Chang, Cheng-Hsiang Shei, I-Yun Lisa Hsieh",
            "status": "submitted",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        },
        {
            "title": "Emission-aware routing for cold-chain last-mile logistics: A data-driven green vehicle routing framework with path-level emission modeling",
            "journal": "Transportation Research Part E: Logistics and Transportation Review",
            "authors": "En-Yi Chou, I-Yun Lisa Hsieh",
            "status": "submitted",
            "year": "'26",
            "month": "Mar.",
            "E3": True
        }
    ]

    # Insert new items at the beginning of the items list of the first section
    data[0]['items'].extend(new_items)

    with open('contents/structures/publications.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    update_publications()
